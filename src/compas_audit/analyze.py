from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

REFERENCE_GROUP = "signal_b"
PRIMARY_TERMS = {
    "signal_a",
    "signal_c",
    "signal_d",
    "nontraditional",
    "has_gap",
    "signal_a_frontline",
    "signal_c_frontline",
    "signal_d_frontline",
    "nontraditional:frontline",
    "has_gap:frontline",
}


def prepare_data(frame: pd.DataFrame, include_failures: bool = False) -> pd.DataFrame:
    required = {
        "signal_group",
        "occupation_tier",
        "education_pathway",
        "career_gap_months",
        "resume_id",
        "temperature",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Input is missing required columns: {sorted(missing)}")

    data = frame.copy()
    if "matched_set_id" not in data:
        data["matched_set_id"] = data.get("template_id", data["resume_id"])
    if "occupation_id" not in data:
        data["occupation_id"] = data.get("template_id", "unknown")
    if "trial" not in data and "trial_number" in data:
        data["trial"] = data["trial_number"]

    data["failed"] = ~data.get("error", pd.Series("", index=data.index)).fillna("").eq("")
    if not include_failures:
        data = data[~data["failed"]].copy()

    data["frontline"] = (data["occupation_tier"] == "frontline").astype(int)
    data["nontraditional"] = (data["education_pathway"] == "nontraditional").astype(int)
    data["has_gap"] = (pd.to_numeric(data["career_gap_months"]) > 0).astype(int)
    for group in ("signal_a", "signal_c", "signal_d"):
        data[group] = (data["signal_group"] == group).astype(int)
        data[f"{group}_frontline"] = data[group] * data["frontline"]

    for outcome in ("fit_score", "recommend", "confidence"):
        if outcome not in data:
            data[outcome] = np.nan
        data[outcome] = pd.to_numeric(data[outcome], errors="coerce")

    if not include_failures:
        data = data.dropna(subset=["fit_score", "recommend", "confidence"])
        if data.empty:
            raise ValueError("No valid audit rows remain after filtering failures.")
        if data["resume_id"].nunique() < 2:
            raise ValueError("Clustered inference requires at least two unique resumes.")
    return data


def model_formula(outcome: str, reference_group: str = REFERENCE_GROUP) -> str:
    if reference_group != "signal_b":
        raise ValueError("The locked design uses signal_b as the reference group.")
    return (
        f"{outcome} ~ signal_a + signal_c + signal_d "
        "+ signal_a_frontline + signal_c_frontline + signal_d_frontline "
        "+ nontraditional + nontraditional:frontline "
        "+ has_gap + has_gap:frontline "
        "+ C(occupation_id) + C(matched_set_id) + C(temperature)"
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


def fit_confidence_model(data: pd.DataFrame, reference_group: str = REFERENCE_GROUP):
    covariance = {"groups": data["resume_id"], "use_correction": True}
    return smf.ols(model_formula("confidence", reference_group), data=data).fit(
        cov_type="cluster", cov_kwds=covariance
    )


def fit_logistic_recommendation(data: pd.DataFrame, reference_group: str = REFERENCE_GROUP):
    return smf.glm(
        model_formula("recommend", reference_group),
        data=data,
        family=sm.families.Binomial(),
    ).fit(cov_type="cluster", cov_kwds={"groups": data["resume_id"]})


def coefficient_frame(
    model: Any,
    outcome: str,
    alpha: float = 0.05,
    model_type: str = "linear",
) -> pd.DataFrame:
    intervals = model.conf_int(alpha=alpha)
    result = pd.DataFrame(
        {
            "outcome": outcome,
            "model_type": model_type,
            "term": model.params.index,
            "estimate": model.params.values,
            "std_error_clustered": model.bse.values,
            "p_value": model.pvalues.values,
            "ci_95_low": intervals.iloc[:, 0].values,
            "ci_95_high": intervals.iloc[:, 1].values,
        }
    )
    tested = result["term"].isin(PRIMARY_TERMS)
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


def placebo_expected_effects(reference_group: str = REFERENCE_GROUP) -> dict[str, float]:
    if reference_group != "signal_b":
        raise ValueError("The locked design uses signal_b as the reference group.")
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
    fit = coefficients[
        coefficients["outcome"].eq("fit_score")
        & coefficients["model_type"].eq("linear")
    ].copy()
    fit = fit[fit["term"].isin(expected)].copy()
    fit["expected_effect"] = fit["term"].map(expected)
    fit["recovery_error"] = fit["estimate"] - fit["expected_effect"]
    fit["abs_recovery_error"] = fit["recovery_error"].abs()
    columns = [
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
    return fit[columns].sort_values("term")


def randomization_inference(
    data: pd.DataFrame,
    permutations: int,
    seed: int = 42,
) -> pd.DataFrame:
    resume_level = (
        data.groupby(["matched_set_id", "resume_id", "signal_group"], as_index=False)
        .agg(mean_fit_score=("fit_score", "mean"))
    )
    observed = (
        resume_level.loc[resume_level["signal_group"].eq("signal_a"), "mean_fit_score"].mean()
        - resume_level.loc[
            resume_level["signal_group"].eq("signal_b"), "mean_fit_score"
        ].mean()
    )
    rng = np.random.default_rng(seed)
    null = np.empty(permutations)
    groups = resume_level["signal_group"].to_numpy()
    sets = resume_level["matched_set_id"].to_numpy()
    scores = resume_level["mean_fit_score"].to_numpy()
    indices_by_set = [
        np.flatnonzero(sets == value) for value in pd.unique(sets)
    ]
    for draw in range(permutations):
        permuted = groups.copy()
        for indices in indices_by_set:
            permuted[indices] = rng.permutation(permuted[indices])
        a_mean = scores[permuted == "signal_a"].mean()
        b_mean = scores[permuted == "signal_b"].mean()
        null[draw] = a_mean - b_mean
    p_value = (1 + np.sum(np.abs(null) >= abs(observed))) / (permutations + 1)
    return pd.DataFrame(
        [
            {
                "contrast": "signal_a_minus_signal_b_fit_score",
                "observed_difference": observed,
                "permutations": permutations,
                "two_sided_p_value": p_value,
            }
        ]
    )


def leave_one_occupation_out(data: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for occupation in sorted(data["occupation_id"].dropna().unique()):
        subset = data[data["occupation_id"].ne(occupation)]
        model, _ = fit_cluster_models(subset)
        for term in sorted(PRIMARY_TERMS):
            if term in model.params:
                rows.append(
                    {
                        "left_out_occupation": occupation,
                        "term": term,
                        "estimate": float(model.params[term]),
                        "std_error": float(model.bse[term]),
                    }
                )
    return pd.DataFrame(rows)


def explanation_theme_counts(data: pd.DataFrame) -> pd.DataFrame:
    text = (
        data.get("reason", pd.Series("", index=data.index)).fillna("")
        + " "
        + data.get("risk_factors", pd.Series("", index=data.index)).fillna("")
    ).str.casefold()
    themes = {
        "experience": r"experience|tenure",
        "skills": r"skill|technical",
        "education": r"education|degree|pathway",
        "career_gap": r"gap|break|continuity",
        "achievement": r"achievement|result|outcome",
        "uncertainty": r"uncertain|validate|depth|risk",
    }
    return pd.DataFrame(
        [
            {
                "theme": theme,
                "mentions": int(text.str.contains(pattern, regex=True).sum()),
                "share_of_valid_responses": float(
                    text.str.contains(pattern, regex=True).mean()
                ),
            }
            for theme, pattern in themes.items()
        ]
    )


def write_report(
    output: Path,
    raw: pd.DataFrame,
    data: pd.DataFrame,
    coefficients: pd.DataFrame,
    recovery: pd.DataFrame,
) -> None:
    failures = int(len(raw) - len(data))
    mean_abs_error = (
        float(recovery["abs_recovery_error"].mean())
        if not recovery.empty
        else float("nan")
    )
    lines = [
        "# Placebo validation report",
        "",
        "This report validates the software and estimator against a deterministic provider. "
        "It is not evidence about Claude, employers, or actual applicants.",
        "",
        "## Validation scale",
        "",
        f"- Evaluations: **{len(raw):,}**",
        f"- Valid evaluations: **{len(data):,}**",
        f"- Failed evaluations: **{failures:,}**",
        f"- Matched resumes: **{data['resume_id'].nunique():,}**",
        f"- Base profiles: **{data['matched_set_id'].nunique():,}**",
        f"- Occupations: **{data['occupation_id'].nunique():,}**",
        "",
        "## Coefficient recovery",
        "",
        f"Mean absolute recovery error: **{mean_abs_error:.3f} fit-score points**.",
        "",
        recovery.to_markdown(index=False),
        "",
        "## Primary model coefficients",
        "",
        coefficients[coefficients["term"].isin(PRIMARY_TERMS)].to_markdown(index=False),
        "",
    ]
    (output / "placebo_validation_report.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def analyze(input_path: str, output_dir: str, reference_group: str = REFERENCE_GROUP) -> None:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(input_path)
    data = prepare_data(raw)
    all_rows = prepare_data(raw, include_failures=True)

    refusal_values = pd.to_numeric(
        raw.get("refusal", pd.Series(0, index=raw.index)), errors="coerce"
    ).fillna(0)
    quality = pd.DataFrame(
        [
            {
                "input_rows": len(raw),
                "valid_rows": len(data),
                "failed_rows": len(raw) - len(data),
                "refusals": int(refusal_values.sum()),
                "unique_observation_ids": (
                    raw["observation_id"].nunique()
                    if "observation_id" in raw
                    else len(raw)
                ),
                "duplicate_observation_ids": (
                    int(raw["observation_id"].duplicated().sum())
                    if "observation_id" in raw
                    else 0
                ),
                "missing_raw_responses": int(
                    raw.get("raw_response", pd.Series("", index=raw.index))
                    .fillna("")
                    .eq("")
                    .sum()
                ),
                "unique_resumes": data["resume_id"].nunique(),
                "unique_matched_sets": data["matched_set_id"].nunique(),
                "unique_occupations": data["occupation_id"].nunique(),
            }
        ]
    )
    quality.to_csv(output / "data_quality.csv", index=False)

    summary = data.groupby(
        ["signal_group", "occupation_tier"], as_index=False
    ).agg(
        mean_fit_score=("fit_score", "mean"),
        recommendation_rate=("recommend", "mean"),
        mean_confidence=("confidence", "mean"),
        observations=("resume_id", "size"),
        unique_resumes=("resume_id", "nunique"),
    )
    summary.to_csv(output / "descriptive_summary.csv", index=False)

    fit_model, lpm_model = fit_cluster_models(data, reference_group)
    confidence_model = fit_confidence_model(data, reference_group)
    model_frames = [
        coefficient_frame(fit_model, "fit_score", model_type="linear"),
        coefficient_frame(lpm_model, "recommend", model_type="linear_probability"),
        coefficient_frame(confidence_model, "confidence", model_type="linear"),
    ]
    (output / "ols_fit_score_clustered.txt").write_text(
        fit_model.summary().as_text(), encoding="utf-8"
    )
    (output / "ols_recommendation_clustered.txt").write_text(
        lpm_model.summary().as_text(), encoding="utf-8"
    )
    (output / "ols_confidence_clustered.txt").write_text(
        confidence_model.summary().as_text(), encoding="utf-8"
    )

    try:
        logit_model = fit_logistic_recommendation(data, reference_group)
        model_frames.append(
            coefficient_frame(logit_model, "recommend", model_type="logistic")
        )
        (output / "logit_recommendation_clustered.txt").write_text(
            logit_model.summary().as_text(), encoding="utf-8"
        )
    except Exception as exc:
        (output / "logit_recommendation_clustered.txt").write_text(
            f"Logistic model did not converge: {type(exc).__name__}: {exc}\n",
            encoding="utf-8",
        )

    coefficients = pd.concat(model_frames, ignore_index=True)
    coefficients.to_csv(output / "model_coefficients.csv", index=False)
    recovery = build_placebo_recovery(coefficients, reference_group)
    recovery.to_csv(output / "placebo_effect_recovery.csv", index=False)

    randomization_inference(data, 999).to_csv(
        output / "randomization_inference.csv", index=False
    )
    leave_one_occupation_out(data).to_csv(
        output / "leave_one_occupation_out.csv", index=False
    )

    failure_sensitivity = pd.DataFrame(
        [
            {
                "specification": "valid_responses_only",
                "recommendation_rate": float(data["recommend"].mean()),
                "rows": len(data),
            },
            {
                "specification": "failed_responses_as_not_recommended",
                "recommendation_rate": float(all_rows["recommend"].fillna(0).mean()),
                "rows": len(all_rows),
            },
        ]
    )
    failure_sensitivity.to_csv(output / "failure_sensitivity.csv", index=False)
    explanation_theme_counts(data).to_csv(
        output / "explanation_themes.csv", index=False
    )
    write_report(output, raw, data, coefficients, recovery)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze audit results with matched-set models and robustness checks."
    )
    parser.add_argument("--input", default="outputs/screening_results.csv")
    parser.add_argument("--output-dir", default="outputs/analysis")
    parser.add_argument("--reference-group", default=REFERENCE_GROUP)
    args = parser.parse_args()
    analyze(args.input, args.output_dir, args.reference_group)
    print(f"Analysis written to {args.output_dir}")


if __name__ == "__main__":
    main()
