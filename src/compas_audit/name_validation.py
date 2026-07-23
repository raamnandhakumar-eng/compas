from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd

from .common import load_config

REGISTRY_COLUMNS = {
    "candidate_id",
    "signal_group",
    "perceived_name_signal",
    "first_name",
    "last_name",
    "full_name",
    "census_first_count",
    "census_first_group_share",
    "census_first_sex_share",
    "census_last_count",
    "census_last_group_share",
    "ssa_frequency",
    "source_year",
    "source_file",
    "screening_status",
}

RESPONSE_COLUMNS = {
    "respondent_id",
    "candidate_id",
    "perceived_race_ethnicity",
    "perceived_gender",
    "familiarity_1_5",
    "perceived_socioeconomic_status_1_5",
    "confidence_1_5",
    "name_unusual_1_5",
    "consent_confirmed",
    "attention_check_passed",
}


def _boolean_series(values: pd.Series) -> pd.Series:
    return values.astype(str).str.strip().str.lower().isin({"true", "1", "yes", "y"})


def _clean_text(value: Any) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().casefold()


def _mode_and_agreement(values: pd.Series) -> tuple[str, float]:
    cleaned = values.dropna().astype(str).str.strip().str.casefold()
    cleaned = cleaned[cleaned.ne("")]
    if cleaned.empty:
        return "", 0.0
    counts = cleaned.value_counts()
    return str(counts.index[0]), float(counts.iloc[0] / counts.sum())


def _range_by_group(summary: pd.DataFrame, value: str, expected_groups: int) -> tuple[float, bool]:
    group_means = summary.groupby("signal_group")[value].mean()
    observed = group_means[group_means.notna()]
    if len(observed) != expected_groups:
        return float("nan"), False
    value_range = float(observed.max() - observed.min())
    return value_range, True


def evaluate_name_signals(
    registry: pd.DataFrame,
    responses: pd.DataFrame,
    settings: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    missing_registry = REGISTRY_COLUMNS - set(registry.columns)
    if missing_registry:
        raise ValueError(f"Name registry is missing columns: {sorted(missing_registry)}")

    missing_responses = RESPONSE_COLUMNS - set(responses.columns)
    if missing_responses:
        raise ValueError(f"Perception responses are missing columns: {sorted(missing_responses)}")

    minimum_respondents = int(settings.get("minimum_respondents", 100))
    minimum_group_agreement = float(settings.get("minimum_group_agreement", 0.70))
    minimum_gender_agreement = float(settings.get("minimum_gender_agreement", 0.70))
    minimum_median_confidence = float(settings.get("minimum_median_confidence", 4.0))
    maximum_ses_range = float(settings.get("maximum_between_group_ses_range", 0.75))
    maximum_familiarity_range = float(
        settings.get("maximum_between_group_familiarity_range", 0.75)
    )
    maximum_unusual_range = float(settings.get("maximum_between_group_unusual_range", 0.75))

    valid = responses[
        _boolean_series(responses["consent_confirmed"])
        & _boolean_series(responses["attention_check_passed"])
    ].copy()

    scale_columns = (
        "familiarity_1_5",
        "perceived_socioeconomic_status_1_5",
        "confidence_1_5",
        "name_unusual_1_5",
    )
    for column in scale_columns:
        valid[column] = pd.to_numeric(valid[column], errors="coerce")

    complete_text = (
        valid["candidate_id"].notna()
        & valid["perceived_race_ethnicity"].notna()
        & valid["perceived_gender"].notna()
    )
    complete_scales = valid[list(scale_columns)].notna().all(axis=1)
    valid_scales = valid[list(scale_columns)].apply(lambda col: col.between(1, 5)).all(axis=1)
    valid = valid[complete_text & complete_scales & valid_scales].copy()

    summaries: list[dict[str, Any]] = []
    for candidate in registry.itertuples(index=False):
        subset = valid[valid["candidate_id"].astype(str).eq(str(candidate.candidate_id))]
        perceived_group, group_agreement = _mode_and_agreement(
            subset["perceived_race_ethnicity"]
        )
        perceived_gender, gender_agreement = _mode_and_agreement(subset["perceived_gender"])
        intended_group = _clean_text(candidate.perceived_name_signal)
        intended_gender = "male"
        source_complete = _clean_text(candidate.screening_status) in {
            "source_screened_pending_pretest",
            "approved",
        }

        summaries.append(
            {
                "candidate_id": candidate.candidate_id,
                "signal_group": candidate.signal_group,
                "full_name": candidate.full_name,
                "perceived_name_signal": candidate.perceived_name_signal,
                "valid_respondents": int(len(subset)),
                "modal_perceived_group": perceived_group,
                "group_agreement": group_agreement,
                "modal_perceived_gender": perceived_gender,
                "gender_agreement": gender_agreement,
                "mean_familiarity": (
                    float(subset["familiarity_1_5"].mean())
                    if not subset.empty
                    else float("nan")
                ),
                "mean_socioeconomic_status": (
                    float(subset["perceived_socioeconomic_status_1_5"].mean())
                    if not subset.empty
                    else float("nan")
                ),
                "median_confidence": (
                    float(subset["confidence_1_5"].median())
                    if not subset.empty
                    else float("nan")
                ),
                "mean_unusual": (
                    float(subset["name_unusual_1_5"].mean())
                    if not subset.empty
                    else float("nan")
                ),
                "source_screen_complete": source_complete,
                "intended_group_match": perceived_group == intended_group,
                "intended_gender_match": perceived_gender == intended_gender,
            }
        )

    summary = pd.DataFrame(summaries)
    expected_groups = int(registry["signal_group"].nunique())
    ses_range, ses_complete = _range_by_group(
        summary, "mean_socioeconomic_status", expected_groups
    )
    familiarity_range, familiarity_complete = _range_by_group(
        summary, "mean_familiarity", expected_groups
    )
    unusual_range, unusual_complete = _range_by_group(
        summary, "mean_unusual", expected_groups
    )

    balance = pd.DataFrame(
        [
            {
                "metric": "perceived_socioeconomic_status",
                "between_group_range": ses_range,
                "maximum_allowed": maximum_ses_range,
                "complete": ses_complete,
                "pass": bool(ses_complete and ses_range <= maximum_ses_range),
            },
            {
                "metric": "familiarity",
                "between_group_range": familiarity_range,
                "maximum_allowed": maximum_familiarity_range,
                "complete": familiarity_complete,
                "pass": bool(
                    familiarity_complete and familiarity_range <= maximum_familiarity_range
                ),
            },
            {
                "metric": "name_unusual",
                "between_group_range": unusual_range,
                "maximum_allowed": maximum_unusual_range,
                "complete": unusual_complete,
                "pass": bool(unusual_complete and unusual_range <= maximum_unusual_range),
            },
        ]
    )
    all_balance_pass = bool(balance["pass"].all())

    summary["approved_for_live_audit"] = (
        summary["source_screen_complete"]
        & summary["valid_respondents"].ge(minimum_respondents)
        & summary["intended_group_match"]
        & summary["group_agreement"].ge(minimum_group_agreement)
        & summary["intended_gender_match"]
        & summary["gender_agreement"].ge(minimum_gender_agreement)
        & summary["median_confidence"].ge(minimum_median_confidence)
        & all_balance_pass
    )
    return summary, balance


def assert_live_name_signals_validated(config: dict[str, Any]) -> None:
    settings = config.get("name_validation", {})
    if not bool(settings.get("required_for_live", True)):
        return

    summary_path = Path(
        settings.get("summary_output", "results/name_validation/name_summary.csv")
    )
    if not summary_path.exists():
        raise RuntimeError(
            "Live audits require validated perceived name signals. Run "
            "compas-validate-names after completing the perception pretest."
        )

    summary = pd.read_csv(summary_path)
    required = {"full_name", "approved_for_live_audit"}
    missing = required - set(summary.columns)
    if missing:
        raise RuntimeError(f"Name-validation summary is missing columns: {sorted(missing)}")

    configured_names = {
        str(name)
        for names in config.get("signals", {}).get("names", {}).values()
        for name in names
    }
    approved = set(
        summary.loc[_boolean_series(summary["approved_for_live_audit"]), "full_name"].astype(str)
    )
    unapproved = sorted(configured_names - approved)
    if unapproved:
        raise RuntimeError(
            "Live audit blocked because these perceived name signals have not passed "
            f"source screening and the perception pretest: {unapproved}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate COMPAS perceived name signals.")
    parser.add_argument("--config", default="config/audit.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    settings = config.get("name_validation", {})
    registry_path = Path(
        settings.get("candidate_registry", "data/name_validation/name_candidates.csv")
    )
    responses_path = Path(
        settings.get("perception_responses", "data/name_validation/perception_responses.csv")
    )
    summary_path = Path(
        settings.get("summary_output", "results/name_validation/name_summary.csv")
    )
    balance_path = Path(
        settings.get("balance_output", "results/name_validation/name_balance_tests.csv")
    )

    registry = pd.read_csv(registry_path)
    responses = pd.read_csv(responses_path)
    summary, balance = evaluate_name_signals(registry, responses, settings)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(summary_path, index=False)
    balance.to_csv(balance_path, index=False)

    approved = int(summary["approved_for_live_audit"].sum())
    print(
        f"Approved {approved} of {len(summary)} perceived name signals; "
        f"wrote {summary_path} and {balance_path}"
    )


if __name__ == "__main__":
    main()
