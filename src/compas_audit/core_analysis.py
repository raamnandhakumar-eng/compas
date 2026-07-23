from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

PRIMARY_TERMS = {
    "nontraditional",
    "has_gap",
    "nontraditional:frontline",
    "has_gap:frontline",
}


def prepare_core_data(frame: pd.DataFrame, include_failures: bool = False) -> pd.DataFrame:
    required = {
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

    error = data.get("error", pd.Series("", index=data.index)).fillna("")
    data["failed"] = ~error.eq("")
    if not include_failures:
        data = data[~data["failed"]].copy()

    data["frontline"] = data["occupation_tier"].eq("frontline").astype(int)
    data["nontraditional"] = data["education_pathway"].eq("nontraditional").astype(int)
    data["has_gap"] = pd.to_numeric(data["career_gap_months"]).gt(0).astype(int)

    for outcome in ("fit_score", "recommend", "confidence"):
        if outcome not in data:
            data[outcome] = np.nan
        data[outcome] = pd.to_numeric(data[outcome], errors="coerce")

    if not include_failures:
        data = data.dropna(subset=["fit_score", "recommend", "confidence"])
        if data.empty:
            raise ValueError("No valid core-audit rows remain after filtering failures.")
        if data["resume_id"].nunique() < 2:
            raise ValueError("Clustered inference requires at least two unique resumes.")
    return data


def core_model_formula(outcome: str) -> str:
    return (
        f"{outcome} ~ nontraditional + has_gap "
        "+ nontraditional:frontline + has_gap:frontline "
        "+ C(occupation_id) + C(matched_set_id) + C(temperature)"
    )


def fit_core_linear_model(data: pd.DataFrame, outcome: str):
    covariance = {"groups": data["resume_id"], "use_correction": True}
    return smf.ols(core_model_formula(outcome), data=data).fit(
        cov_type="cluster",
        cov_kwds=covariance,
    )


def fit_core_logistic_recommendation(data: pd.DataFrame):
    if data["recommend"].nunique() < 2:
        return None
    return smf.glm(
        core_model_formula("recommend"),
        data=data,
        family=sm.families.Binomial(),
    ).fit(cov_type="cluster", cov_kwds={"groups": data["resume_id"]})


def coefficient_frame(
    model: Any,
    outcome: str,
    model_type: str,
) -> pd.DataFrame:
    intervals = model.conf_int(alpha=0.05)
    return pd.DataFrame(
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


def apply_fdr(coefficients: pd.DataFrame, alpha: float = 0.05) -> pd.DataFrame:
    result = coefficients.copy()
    result["q_value_bh"] = pd.NA
    result["reject_fdr_05"] = False
    tested = result["term"].isin(PRIMARY_TERMS)
    if tested.any():
        reject, q_values, _, _ = multipletests(
            result.loc[tested, "p_value"],
            alpha=alpha,
            method="fdr_bh",
        )
        result.loc[tested, "q_value_bh"] = q_values
        result.loc[tested, "reject_fdr_05"] = reject
    return result


def placebo_recovery(coefficients: pd.DataFrame) -> pd.DataFrame:
    expected = {
        "nontraditional": -0.15,
        "has_gap": -0.45,
        "nontraditional:frontline": 0.0,
        "has_gap:frontline": 0.0,
    }
    fit = coefficients[
        coefficients["outcome"].eq("fit_score")
        & coefficients["model_type"].eq("linear")
        & coefficients["term"].isin(expected)
    ].copy()
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


def treatment_means(data: pd.DataFrame) -> pd.DataFrame:
    return (
        data.groupby(
            ["occupation_tier", "education_pathway", "career_gap_months"],
            as_index=False,
        )
        .agg(
            evaluations=("observation_id", "size")
            if "observation_id" in data
            else ("resume_id", "size"),
            mean_fit_score=("fit_score", "mean"),
            interview_rate=("recommend", "mean"),
            mean_confidence=("confidence", "mean"),
        )
        .sort_values(
            ["occupation_tier", "education_pathway", "career_gap_months"]
        )
    )


def failure_sensitivity(data_with_failures: pd.DataFrame) -> pd.DataFrame:
    sensitivity = data_with_failures.copy()
    sensitivity["recommend_failed_as_zero"] = sensitivity["recommend"].fillna(0)
    if sensitivity["recommend_failed_as_zero"].nunique() < 2:
        return pd.DataFrame(
            columns=[
                "outcome",
                "model_type",
                "term",
                "estimate",
                "std_error_clustered",
                "p_value",
                "ci_95_low",
                "ci_95_high",
            ]
        )
    covariance = {"groups": sensitivity["resume_id"], "use_correction": True}
    model = smf.ols(
        core_model_formula("recommend_failed_as_zero"),
        data=sensitivity,
    ).fit(cov_type="cluster", cov_kwds=covariance)
    return coefficient_frame(
        model,
        outcome="recommend_failed_as_zero",
        model_type="linear_sensitivity",
    )


def write_report(
    output: Path,
    raw: pd.DataFrame,
    data: pd.DataFrame,
    coefficients: pd.DataFrame,
    recovery: pd.DataFrame,
) -> None:
    primary = coefficients[coefficients["term"].isin(PRIMARY_TERMS)]
    mean_abs_error = (
        float(recovery["abs_recovery_error"].mean())
        if not recovery.empty
        else float("nan")
    )
    lines = [
        "# Core labor-market audit report",
        "",
        "This track tests career-gap and education-pathway effects while holding "
        "candidate names fixed within matched sets. It does not estimate "
        "perceived-name-signal effects.",
        "",
        "## Run quality",
        "",
        f"- Evaluations attempted: **{len(raw):,}**",
        f"- Valid evaluations: **{len(data):,}**",
        f"- Failed evaluations: **{len(raw) - len(data):,}**",
        f"- Unique matched resumes: **{data['resume_id'].nunique():,}**",
        f"- Base profiles: **{data['matched_set_id'].nunique():,}**",
        f"- Occupations: **{data['occupation_id'].nunique():,}**",
        f"- Recommendation model estimable: **{'Yes' if data['recommend'].nunique() >= 2 else 'No'}**",
        "",
        "## Primary coefficients",
        "",
        primary.to_markdown(index=False),
        "",
    ]
    if not recovery.empty:
        lines.extend(
            [
                "## Mock-provider recovery diagnostic",
                "",
                "This section is meaningful only for the deterministic mock provider.",
                "",
                f"Mean absolute recovery error: **{mean_abs_error:.3f}**.",
                "",
                recovery.to_markdown(index=False),
                "",
            ]
        )
    (output / "core_audit_report.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def analyze_core(input_path: str, output_dir: str, fdr_alpha: float = 0.05) -> None:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(input_path)
    data = prepare_core_data(raw)
    all_rows = prepare_core_data(raw, include_failures=True)

    models = [
        (fit_core_linear_model(data, "fit_score"), "fit_score", "linear"),
        (fit_core_linear_model(data, "confidence"), "confidence", "linear"),
    ]
    recommendation_estimable = data["recommend"].nunique() >= 2
    if recommendation_estimable:
        models.append(
            (fit_core_linear_model(data, "recommend"), "recommend", "linear")
        )
        logistic = fit_core_logistic_recommendation(data)
        if logistic is not None:
            models.append((logistic, "recommend", "logistic"))

    coefficients = pd.concat(
        [
            coefficient_frame(model, outcome, model_type)
            for model, outcome, model_type in models
        ],
        ignore_index=True,
    )
    coefficients = apply_fdr(coefficients, alpha=fdr_alpha)
    recovery = placebo_recovery(coefficients)
    sensitivity = failure_sensitivity(all_rows)

    quality = pd.DataFrame(
        [
            {
                "input_rows": len(raw),
                "valid_rows": len(data),
                "failed_rows": len(raw) - len(data),
                "unique_resumes": data["resume_id"].nunique(),
                "unique_base_profiles": data["matched_set_id"].nunique(),
                "unique_occupations": data["occupation_id"].nunique(),
                "name_signal_effects_estimated": False,
                "recommendation_models_estimable": recommendation_estimable,
            }
        ]
    )

    coefficients.to_csv(output / "core_coefficients.csv", index=False)
    recovery.to_csv(output / "core_placebo_recovery.csv", index=False)
    sensitivity.to_csv(output / "core_failure_sensitivity.csv", index=False)
    treatment_means(data).to_csv(output / "core_treatment_means.csv", index=False)
    quality.to_csv(output / "core_run_quality.csv", index=False)
    write_report(output, raw, data, coefficients, recovery)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze the career-gap and education-pathway core audit."
    )
    parser.add_argument(
        "--input",
        default="outputs/core/screening_results.csv",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/core/analysis",
    )
    parser.add_argument("--fdr-alpha", type=float, default=0.05)
    args = parser.parse_args()
    analyze_core(args.input, args.output_dir, fdr_alpha=args.fdr_alpha)


if __name__ == "__main__":
    main()
