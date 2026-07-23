import pandas as pd

from compas_audit.name_validation import evaluate_name_signals


def _responses(registry: pd.DataFrame, n: int = 100) -> pd.DataFrame:
    rows = []
    for candidate in registry.itertuples(index=False):
        for respondent in range(n):
            rows.append(
                {
                    "respondent_id": f"{candidate.candidate_id}-r{respondent:03d}",
                    "candidate_id": candidate.candidate_id,
                    "perceived_race_ethnicity": candidate.perceived_name_signal,
                    "perceived_gender": "male",
                    "familiarity_1_5": 2,
                    "perceived_socioeconomic_status_1_5": 3,
                    "confidence_1_5": 4,
                    "name_unusual_1_5": 2,
                    "consent_confirmed": True,
                    "attention_check_passed": True,
                }
            )
    return pd.DataFrame(rows)


def test_source_registry_is_populated_and_not_rare():
    registry = pd.read_csv("data/name_validation/name_candidates.csv")
    assert registry.groupby("signal_group").size().eq(2).all()
    assert registry["census_first_count"].ge(100).all()
    assert registry["census_last_count"].ge(100).all()
    assert registry["ssa_frequency"].ge(100).all()
    assert registry["screening_status"].eq("source_screened_pending_pretest").all()


def test_predeclared_thresholds_approve_balanced_responses():
    registry = pd.read_csv("data/name_validation/name_candidates.csv")
    settings = {
        "minimum_respondents": 100,
        "minimum_group_agreement": 0.70,
        "minimum_gender_agreement": 0.70,
        "minimum_median_confidence": 4.0,
        "maximum_between_group_ses_range": 0.75,
        "maximum_between_group_familiarity_range": 0.75,
        "maximum_between_group_unusual_range": 0.75,
    }
    summary, balance = evaluate_name_signals(registry, _responses(registry), settings)
    assert summary["approved_for_live_audit"].all()
    assert balance["pass"].all()


def test_empty_pretest_never_approves_names():
    registry = pd.read_csv("data/name_validation/name_candidates.csv")
    empty = pd.read_csv("data/name_validation/perception_responses.csv")
    summary, balance = evaluate_name_signals(registry, empty, {})
    assert not summary["approved_for_live_audit"].any()
    assert not balance["pass"].any()
