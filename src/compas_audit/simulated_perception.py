from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from .common import load_config
from .name_validation import evaluate_name_signals

DATA_ORIGIN = "simulated_pipeline_test"
DEFAULT_RESPONSES = Path(
    "data/simulated/name_validation/perception_responses_simulated.csv"
)
DEFAULT_SUMMARY = Path(
    "results/simulated/name_validation/name_summary_simulated.csv"
)
DEFAULT_BALANCE = Path(
    "results/simulated/name_validation/name_balance_tests_simulated.csv"
)
DEFAULT_MANIFEST = Path(
    "results/simulated/name_validation/simulation_manifest.json"
)


def _bucket(seed: int, respondent: int, candidate_id: str, field: str) -> int:
    payload = f"{seed}|{respondent}|{candidate_id}|{field}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 100


def generate_simulated_responses(
    registry: pd.DataFrame,
    respondents: int = 120,
    seed: int = 20260723,
    invalid_respondents: int = 4,
) -> pd.DataFrame:
    """Generate deterministic responses for testing the pretest pipeline."""
    if respondents - invalid_respondents < 100:
        raise ValueError("The simulation must retain at least 100 valid respondents.")

    signal_labels = list(dict.fromkeys(registry["perceived_name_signal"].astype(str)))
    rows: list[dict[str, object]] = []

    for respondent in range(1, respondents + 1):
        attention_passed = respondent <= respondents - invalid_respondents
        for candidate in registry.itertuples(index=False):
            intended = str(candidate.perceived_name_signal)
            group_bucket = _bucket(seed, respondent, candidate.candidate_id, "group")
            if group_bucket < 82:
                perceived_group = intended
            else:
                alternatives = [
                    value for value in signal_labels + ["Other or unsure"] if value != intended
                ]
                perceived_group = alternatives[group_bucket % len(alternatives)]

            gender_bucket = _bucket(seed, respondent, candidate.candidate_id, "gender")
            if gender_bucket < 93:
                perceived_gender = "Male"
            elif gender_bucket < 97:
                perceived_gender = "Female"
            else:
                perceived_gender = "Unsure"

            scale_bucket = _bucket(seed, respondent, candidate.candidate_id, "scales")
            familiarity = 2 + scale_bucket % 3
            socioeconomic_status = 2 + (scale_bucket // 3) % 3
            confidence = (
                4 + (scale_bucket // 9) % 2
                if perceived_group == intended
                else 3 + (scale_bucket // 9) % 2
            )
            unusual = 2 + (scale_bucket // 18) % 3

            rows.append(
                {
                    "respondent_id": f"sim_{respondent:03d}",
                    "candidate_id": candidate.candidate_id,
                    "perceived_race_ethnicity": perceived_group,
                    "perceived_gender": perceived_gender,
                    "familiarity_1_5": familiarity,
                    "perceived_socioeconomic_status_1_5": socioeconomic_status,
                    "confidence_1_5": confidence,
                    "name_unusual_1_5": unusual,
                    "consent_confirmed": True,
                    "attention_check_passed": attention_passed,
                    "data_origin": DATA_ORIGIN,
                    "simulation_seed": seed,
                }
            )

    return pd.DataFrame(rows)


def evaluate_simulation(
    registry: pd.DataFrame,
    responses: pd.DataFrame,
    settings: dict[str, object],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Apply the real threshold code without granting live-audit approval."""
    summary, balance = evaluate_name_signals(registry, responses, settings)

    threshold_pass = summary["approved_for_live_audit"].astype(bool)
    summary["passes_preregistered_thresholds_in_simulation"] = threshold_pass
    summary["approved_for_live_audit"] = False
    summary["data_origin"] = DATA_ORIGIN
    summary["eligible_for_live_audit"] = False

    balance["data_origin"] = DATA_ORIGIN
    balance["eligible_for_live_audit"] = False
    return summary, balance


def write_simulation(
    config_path: str,
    respondents: int,
    seed: int,
    responses_output: Path,
    summary_output: Path,
    balance_output: Path,
    manifest_output: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    config = load_config(config_path)
    settings = config.get("name_validation", {})
    registry_path = Path(
        settings.get("candidate_registry", "data/name_validation/name_candidates.csv")
    )
    registry = pd.read_csv(registry_path)

    responses = generate_simulated_responses(registry, respondents=respondents, seed=seed)
    summary, balance = evaluate_simulation(registry, responses, settings)

    for output in (responses_output, summary_output, balance_output, manifest_output):
        output.parent.mkdir(parents=True, exist_ok=True)

    responses.to_csv(responses_output, index=False)
    summary.to_csv(summary_output, index=False)
    balance.to_csv(balance_output, index=False)
    response_sha256 = hashlib.sha256(responses_output.read_bytes()).hexdigest()

    manifest = {
        "data_origin": DATA_ORIGIN,
        "simulation_seed": seed,
        "panel_respondents": respondents,
        "response_rows": int(len(responses)),
        "valid_responses_per_name": int(
            responses.loc[responses["attention_check_passed"]]
            .groupby("candidate_id")
            .size()
            .min()
        ),
        "response_csv_sha256": response_sha256,
        "real_respondents": 0,
        "eligible_for_live_audit": False,
        "production_survey_file_modified": False,
        "production_validation_outputs_modified": False,
    }
    manifest_output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return responses, summary, balance


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a simulated name-perception study for pipeline testing."
    )
    parser.add_argument("--config", default="config/audit.yaml")
    parser.add_argument("--respondents", type=int, default=120)
    parser.add_argument("--seed", type=int, default=20260723)
    parser.add_argument("--responses-output", type=Path, default=DEFAULT_RESPONSES)
    parser.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--balance-output", type=Path, default=DEFAULT_BALANCE)
    parser.add_argument("--manifest-output", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()

    responses, summary, _ = write_simulation(
        args.config,
        args.respondents,
        args.seed,
        args.responses_output,
        args.summary_output,
        args.balance_output,
        args.manifest_output,
    )
    passed = int(summary["passes_preregistered_thresholds_in_simulation"].sum())
    print(
        f"Wrote {len(responses)} simulated response rows; "
        f"{passed} of {len(summary)} names pass thresholds in simulation. "
        "Live-audit approval remains false."
    )


if __name__ == "__main__":
    main()
