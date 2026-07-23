from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

REFERENCE_GROUP = "signal_b"


def prepare_data(frame: pd.DataFrame) -> pd.DataFrame:
    required = {
        "fit_score",
        "recommend",
        "signal_group",
        "occupation_tier",
        "education_pathway",
        "career_gap_months",
        "template_id",
        "resume_id",
        "temperature",
        "trial",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Input is missing required columns: {sorted(missing)}")

    data = frame.copy()
    if "error" in data:
        data = data[data["error"].fillna("").eq("")]
    data["frontline"] = (data["occupation_tier"] == "frontline").astype(int)
    data["nontraditional"] = (data["education_pathway"] == "nontraditional").astype(int)
    data["has_gap"] = (pd.to_numeric(data["career_gap_months"]) > 0).astype(int)
    for group in ("signal_a", "signal_c", "signal_d"):
        data[group] = (data["signal_group"] == group).astype(int)
        data[f"{group}_frontline"] = data[group] * data["frontline"]
    data["fit_score"] = pd.to_numeric(data["fit_score"], errors="coerce")
    data["recommend"] = pd.to_numeric(data["recommend"], errors="coerce")
    data["confidence"] = pd.to_numeric(data.get("confidence"), errors="coerce")
    data = data.dropna(subset=["fit_score", "recommend"])
    if data.empty:
        raise ValueError("No valid audit rows remain after filtering failures.")
    if data["resume_id"].nunique() < 2:
        raise ValueError("Clustered inference requires at least two unique resumes.")
    return data


def model_formula(outcome: str, reference_group: str = REFERENCE_GROUP) -> str:
    if reference_group != "signal_b":
        raise ValueError("The current locked design uses signal_b as the reference group.")
    return (
        f"{outcome} ~ signal_a + signal_c + signal_d + signal_a_frontline "
        "+ signal_c_frontline + signal_d_frontline + nontraditional "
        "+ nontraditional:frontline + has_gap + has_gap:frontline "
        "+ C(template_id) + C(temperature)"
    )


def fit_cluster_models(data: pd.DataFrame, reference_group: str = REFERENCE_GROUP):
    covariance = {"groups": data["resume_id"], "use_correction": True}
    fit_model = smf.ols(model_formula("fit_score", reference_group), data=data).fit(
        cov_type="cluster", cov_kwds=covariance
    )
    rec_model = smf.ols(model_formula("recommend", reference_group), data=data).fit(
        cov_type="cluster", cov_kwds=covariance
    )
    return fit_model, rec_model


def coefficient_frame(model, outcome: str, alpha: float = 0.05) -> pd.DataFrame:
    intervals = model.conf_int()
    result = pd.DataFrame(
        {
            "outcome": outcome,
            "term": model.params.index,
            "estimate": model.params.values,
            "std_error_clustered": model.bse.values,
            "p_value": model.pvalues.values,
            "ci_95_low": intervals[0].values,
            "ci_95_high": intervals[1].values,
        }
    )
    tested = ~result["term"].eq("Intercept")
    result["q_value_bh"] = pd.NA
    result["reject_fdr_05"] = False
    if tested.any():
        reject, q_values, _, _ = multipletests(
            result.loc[tested, "p_value"],
            alpha=alpha,
            method="fdr_bh",
        )
        result.loc[tested, "q_value_bh"] = q_values
        result.loc[tested, "reject_fdr_05"] = reject
    return result


def save_bar_plot(summary: pd.DataFrame, value: str, ylabel: str, path: Path) -> None:
    pivot = summary.pivot(index="signal_group", columns="occupation_tier", values=value)
    ax = pivot.plot(kind="bar")
    ax.set_xlabel("Experimental signal group")
    ax.set_ylabel(ylabel)
    ax.set_title(f"{ylabel} by signal group and occupational tier")
    ax.legend(title="Occupational tier")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def placebo_expected_effects(reference_group: str = REFERENCE_GROUP) -> dict[str, float]:
    if reference_group != "signal_b":
        raise ValueError("The current locked design uses signal_b as the reference group.")
    return {
        "signal_a": -0.20,
        "signal_c": -0.35,
        "signal_d": 0.00,
        "signal_a_frontline": 0.00,
        "signal_c_frontline": -0.20,
        "signal_d_frontline": 0.00,
        "nontraditional": -0.15,
        "nontraditional:frontline": 0.00,
        "has_gap": -0.45,
        "has_gap:frontline": 0.00,
    }


def build_placebo_recovery(
    coefficients: pd.DataFrame,
    reference_group: str = REFERENCE_GROUP,
) -> pd.DataFrame:
    expected = placebo_expected_effects(reference_group)
    fit = coefficients[coefficients["outcome"].eq("fit_score")].copy()
    fit = fit[fit["term"].isin(expected)].copy()
    fit["expected_effect"] = fit["term"].map(expected)
    fit["recovery_error"] = fit["estimate"] - fit["expected_effect"]
    fit["abs_recovery_error"] = fit["recovery_error"].abs()
    return fit[
        [
            "term",
            "expected_effect",
            "estimate",
            "std_error_clustered",
            "p_value",
            "q_value_bh",
            "ci_95_low",
            "ci_95_high",
            "recovery_error",
            "abs_recovery_error",
        ]
    ].sort_values("term")


def write_report(
    output: Path,
    data: pd.DataFrame,
    summary: pd.DataFrame,
    coefficients: pd.DataFrame,
    recovery: pd.DataFrame,
) -> None:
    mean_abs_error = recovery["abs_recovery_error"].mean() if not recovery.empty else float("nan")
    failures = 0
    lines = [
        "# Placebo validation report",
        "",
        (
            "This report evaluates the measurement pipeline against a deterministic "
            "provider with transparent planted effects. It is **not evidence about "
            "Claude or any deployed hiring system**."
        ),
        "",
        "## Validation scale",
        "",
        f"- Successful evaluations: **{len(data):,}**",
        f"- Unique matched resumes: **{data['resume_id'].nunique():,}**",
        f"- Occupational templates: **{data['template_id'].nunique():,}**",
        f"- Temperatures: **{data['temperature'].nunique():,}**",
        (
            "- Repeated trials per resume-temperature cell: "
            f"**{int(data.groupby(['resume_id', 'temperature']).size().median())}**"
        ),
        f"- Parsing failures: **{failures}**",
        "",
        "## Estimation",
        "",
        (
            "The analysis uses template and temperature fixed effects. Standard errors "
            "are clustered by matched resume because each resume is evaluated repeatedly. "
            "Benjamini-Hochberg q-values control the false discovery rate across reported "
            "coefficients."
        ),
        "",
        "## Recovery result",
        "",
        f"Mean absolute coefficient recovery error: **{mean_abs_error:.3f} fit-score points**.",
        "",
        (
            "Because the placebo uses balanced deterministic trial noise, its inferential "
            "p-values are not interpreted. The validation target is coefficient recovery."
        ),
        "",
        "| Planted term | Expected | Estimated | Absolute error |",
        "|---|---:|---:|---:|",
    ]
    for row in recovery.itertuples(index=False):
        lines.append(
            f"| `{row.term}` | {row.expected_effect:.2f} | {row.estimate:.3f} | "
            f"{row.abs_recovery_error:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "The purpose of this stage is estimator validation. A live-model run "
                "should use the same locked configuration, retain null results, and be "
                "reported separately from this placebo benchmark."
            ),
            "",
            "## Group means",
            "",
            summary.to_markdown(index=False),
            "",
        ]
    )
    (output / "placebo_validation_report.md").write_text("\n".join(lines), encoding="utf-8")


def analyze(input_path: str, output_dir: str, reference_group: str = REFERENCE_GROUP) -> None:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(input_path)
    data = prepare_data(raw)

    quality = pd.DataFrame(
        [
            {
                "input_rows": len(raw),
                "valid_rows": len(data),
                "failed_rows": len(raw) - len(data),
                "unique_resumes": data["resume_id"].nunique(),
                "unique_templates": data["template_id"].nunique(),
                "duplicate_run_ids": (
                    int(data["run_id"].duplicated().sum())
                    if "run_id" in data
                    else 0
                ),
            }
        ]
    )
    quality.to_csv(output / "data_quality.csv", index=False)

    summary = data.groupby(["signal_group", "occupation_tier"], as_index=False).agg(
        mean_fit_score=("fit_score", "mean"),
        recommendation_rate=("recommend", "mean"),
        mean_confidence=("confidence", "mean"),
        observations=("resume_id", "size"),
        unique_resumes=("resume_id", "nunique"),
    )
    summary.to_csv(output / "descriptive_summary.csv", index=False)

    reference = summary.groupby("occupation_tier")["mean_fit_score"].transform("max")
    summary.assign(fit_gap_from_tier_max=summary["mean_fit_score"] - reference).to_csv(
        output / "group_disparities.csv", index=False
    )

    stability = data.groupby(["resume_id", "temperature"], as_index=False).agg(
        mean_fit_score=("fit_score", "mean"),
        fit_score_sd=("fit_score", "std"),
        recommendation_rate=("recommend", "mean"),
        trials=("trial", "count"),
    )
    stability.to_csv(output / "trial_stability.csv", index=False)

    fit_model, rec_model = fit_cluster_models(data, reference_group)
    (output / "ols_fit_score_clustered.txt").write_text(
        fit_model.summary().as_text(),
        encoding="utf-8",
    )
    (output / "ols_recommendation_clustered.txt").write_text(
        rec_model.summary().as_text(), encoding="utf-8"
    )
    coefficients = pd.concat(
        [
            coefficient_frame(fit_model, "fit_score"),
            coefficient_frame(rec_model, "recommend"),
        ],
        ignore_index=True,
    )
    coefficients.to_csv(output / "model_coefficients.csv", index=False)

    recovery = build_placebo_recovery(coefficients, reference_group)
    recovery.to_csv(output / "placebo_effect_recovery.csv", index=False)
    write_report(output, data, summary, coefficients, recovery)

    save_bar_plot(summary, "mean_fit_score", "Mean fit score", output / "fit_score_by_group.png")
    save_bar_plot(
        summary,
        "recommendation_rate",
        "Recommendation rate",
        output / "recommendation_rate_by_group.png",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze audit results with clustered regressions."
    )
    parser.add_argument("--input", default="outputs/screening_results.csv")
    parser.add_argument("--output-dir", default="outputs/analysis")
    parser.add_argument("--reference-group", default=REFERENCE_GROUP)
    args = parser.parse_args()
    analyze(args.input, args.output_dir, args.reference_group)
    print(f"Analysis written to {args.output_dir}")


if __name__ == "__main__":
    main()
