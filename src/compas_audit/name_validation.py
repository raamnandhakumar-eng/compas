from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd

from .common import load_config

REGISTRY_COLUMNS = {
    "candidate_id",
    "signal_group",
    "full_name",
    "intended_perceived_group",
    "intended_perceived_gender",
    "source_screen_complete",
}

RESPONSE_COLUMNS = {
    "respondent_id",
    "candidate_id",
    "perceived_race_ethnicity",
    "perceived_gender",
    "familiarity_1_5",
    "socioeconomic_impression_1_5",
    "confidence_1_5",
    "consent_confirmed",
    "attention_check_passed",
}


def _boolean_series(values: pd.Series) -> pd.Series:
    return values.astype(str).str.strip().str.lower().isin({"true", "1", "yes", "y"})


def _mode_and_agreement(values: pd.Series) -> tuple[str, float]:
    cleaned = values.dropna().astype(str).str.strip()
    cleaned = cleaned[cleaned.ne("")]
    if cleaned.empty:
        return "", 0.0
    counts = cleaned.value_counts()
    return str(counts.index[0]), float(counts.iloc[0] / counts.sum())


def evaluate_name_signals(
    registry: pd.DataFrame,
    responses: pd.DataFrame,
    settings: dict[str, Any],
) -> pd.DataFrame:
    missing_registry = REGISTRY_COLUMNS - set(registry.columns)
    if missing_registry:
        raise ValueError(f"Name registry is missing columns: {sorted(missing_registry)}")

    missing_responses = RESPONSE_COLUMNS - set(responses.columns)
    if missing_responses:
        raise ValueError(f"Perception responses are missing columns: {sorted(missing_responses)}")

    minimum_respondents = int(settings.get("minimum_respondents", 100))
    minimum_group_agreement = float(settings.get("minimum_group_agreement", 0.80))
    minimum_gender_agreement = float(settings.get("minimum_gender_agreement", 0.80))
    minimum_mean_confidence = float(settings.get("minimum_mean_confidence", 3.5))
    maximum_mean_familiarity = float(settings.get("maximum_mean_familiarity", 3.0))
    maximum_ses_range = float(settings.get("maximum_between_group_ses_range", 0.75))

    valid = responses[
        _boolean_series(responses["consent_confirmed"])
        & _boolean_series(responses["attention_check_passed"])
    ].copy()

    for column in ("familiarity_1_5", "socioeconomic_impression_1_5", "confidence_1_5"):
        valid[column] = pd.to_numeric(valid[column], errors="coerce")

    summaries: list[dict[str, Any]] = []
    for candidate in registry.itertuples(index=False):
        subset = valid[valid["candidate_id"].astype(str).eq(str(candidate.candidate_id))]
        perceived_group, group_agreement = _mode_and_agreement(
            subset["perceived_race_ethnicity"]
        )
        perceived_gender, gender_agreement = _mode_and_agreement(subset["perceived_gender"])

        intended_group = str(candidate.intended_perceived_group).strip()
        intended_gender = str(candidate.intended_perceived_gender).strip()
        source_complete = str(candidate.source_screen_complete).strip().lower() in {
            "true",
            "1",
            "yes",
            "y",
        }

        mean_familiarity = float(subset["familiarity_1_5"].mean()) if not subset.empty else 0.0
        mean_ses = (
            float(subset["socioeconomic_impression_1_5"].mean()) if not subset.empty else 0.0
        )
        mean_confidence = float(subset["confidence_1_5"].mean()) if not subset.empty else 0.0

        summaries.append(
            {
                "candidate_id": candidate.candidate_id,
                "signal_group": candidate.signal_group,
                "full_name": candidate.full_name,
                "valid_respondents": int(len(subset)),
                "intended_perceived_group": intended_group,
                "modal_perceived_group": perceived_group,
                "group_agreement": group_agreement,
                "intended_perceived_gender": intended_gender,
                "modal_perceived_gender": perceived_gender,
                "gender_agreement": gender_agreement,
                "mean_familiarity": mean_familiarity,
                "mean_socioeconomic_impression": mean_ses,
                "mean_confidence": mean_confidence,
                "source_screen_complete": source_complete,
            }
        )

    summary = pd.DataFrame(summaries)
    group_ses = summary.groupby("signal_group")["mean_socioeconomic_impression"].mean()
    observed_ses = group_ses[group_ses.gt(0)]
    ses_range = float(observed_ses.max() - observed_ses.min()) if len(observed_ses) > 1 else 0.0
    ses_balance_pass = bool(len(observed_ses) > 1 and ses_range <= maximum_ses_range)

    summary["ses_range_across_signal_groups"] = ses_range
    summary["ses_balance_pass"] = ses_balance_pass
    summary["approved_for_live_audit"] = (
        summary["source_screen_complete"]
        & summary["valid_respondents"].ge(minimum_respondents)
        & summary["intended_perceived_group"].ne("")
        & summary["modal_perceived_group"].eq(summary["intended_perceived_group"])
        & summary["group_agreement"].ge(minimum_group_agreement)
        & summary["intended_perceived_gender"].ne("")
        & summary["modal_perceived_gender"].eq(summary["intended_perceived_gender"])
        & summary["gender_agreement"].ge(minimum_gender_agreement)
        & summary["mean_confidence"].ge(minimum_mean_confidence)
        & summary["mean_familiarity"].le(maximum_mean_familiarity)
        & summary["ses_balance_pass"]
    )
    return summary


def assert_live_name_signals_validated(config: dict[str, Any]) -> None:
    settings = config.get("name_validation", {})
    if not bool(settings.get("required_for_live", True)):
        return

    summary_path = Path(
        settings.get("summary_output", "outputs/name_validation_summary.csv")
    )
    if not summary_path.exists():
        raise RuntimeError(
            "Live audits require validated name signals. Run compas-validate-names "
            "after completing the perception pretest."
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
            "Live audit blocked because these names have not passed source screening and "
            f"the perception pretest: {unapproved}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate COMPAS name signals.")
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
    output_path = Path(settings.get("summary_output", "outputs/name_validation_summary.csv"))

    registry = pd.read_csv(registry_path)
    responses = pd.read_csv(responses_path)
    summary = evaluate_name_signals(registry, responses, settings)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_path, index=False)

    approved = int(summary["approved_for_live_audit"].sum())
    print(f"Approved {approved} of {len(summary)} names; wrote {output_path}")


if __name__ == "__main__":
    main()
