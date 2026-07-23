from pathlib import Path

import pandas as pd
import pytest

from compas_audit.name_validation import (
    assert_live_name_signals_validated,
    evaluate_name_signals,
)


def sample_registry() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "candidate_id": "a",
                "signal_group": "signal_a",
                "full_name": "Name A",
                "intended_perceived_group": "group a",
                "intended_perceived_gender": "woman",
                "source_screen_complete": True,
            },
            {
                "candidate_id": "b",
                "signal_group": "signal_b",
                "full_name": "Name B",
                "intended_perceived_group": "group b",
                "intended_perceived_gender": "woman",
                "source_screen_complete": True,
            },
            {
                "candidate_id": "c",
                "signal_group": "signal_c",
                "full_name": "Name C",
                "intended_perceived_group": "group c",
                "intended_perceived_gender": "man",
                "source_screen_complete": True,
            },
            {
                "candidate_id": "d",
                "signal_group": "signal_d",
                "full_name": "Name D",
                "intended_perceived_group": "group d",
                "intended_perceived_gender": "man",
                "source_screen_complete": True,
            },
        ]
    )


def sample_responses(weak_candidate: str | None = None) -> pd.DataFrame:
    rows = []
    groups = {
        "a": ("group a", "woman", 3.0),
        "b": ("group b", "woman", 3.1),
        "c": ("group c", "man", 3.2),
        "d": ("group d", "man", 3.3),
    }
    for candidate_id, (group, gender, socioeconomic_score) in groups.items():
        for respondent in range(100):
            perceived_group = group
            if candidate_id == weak_candidate and respondent >= 70:
                perceived_group = "other group"
            rows.append(
                {
                    "respondent_id": f"{candidate_id}-{respondent}",
                    "candidate_id": candidate_id,
                    "perceived_race_ethnicity": perceived_group,
                    "perceived_gender": gender,
                    "familiarity_1_5": 2,
                    "socioeconomic_impression_1_5": socioeconomic_score,
                    "confidence_1_5": 4.5,
                    "consent_confirmed": True,
                    "attention_check_passed": True,
                }
            )
    return pd.DataFrame(rows)


def test_strong_perception_pretest_approves_names():
    summary = evaluate_name_signals(sample_registry(), sample_responses(), {})
    assert summary["approved_for_live_audit"].all()
    assert summary["valid_respondents"].eq(100).all()


def test_weak_group_agreement_rejects_name():
    summary = evaluate_name_signals(
        sample_registry(),
        sample_responses(weak_candidate="a"),
        {},
    ).set_index("candidate_id")
    assert summary.loc["a", "group_agreement"] == pytest.approx(0.70)
    assert not bool(summary.loc["a", "approved_for_live_audit"])


def test_live_gate_requires_every_configured_name(tmp_path: Path):
    summary_path = tmp_path / "name_validation_summary.csv"
    pd.DataFrame(
        [
            {"full_name": "Name A", "approved_for_live_audit": True},
            {"full_name": "Name B", "approved_for_live_audit": False},
        ]
    ).to_csv(summary_path, index=False)

    config = {
        "name_validation": {
            "required_for_live": True,
            "summary_output": str(summary_path),
        },
        "signals": {"names": {"signal_a": ["Name A"], "signal_b": ["Name B"]}},
    }

    with pytest.raises(RuntimeError, match="Name B"):
        assert_live_name_signals_validated(config)

    pd.DataFrame(
        [
            {"full_name": "Name A", "approved_for_live_audit": True},
            {"full_name": "Name B", "approved_for_live_audit": True},
        ]
    ).to_csv(summary_path, index=False)
    assert_live_name_signals_validated(config)
