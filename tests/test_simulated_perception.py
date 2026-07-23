from pathlib import Path

import pandas as pd

from compas_audit.simulated_perception import (
    DATA_ORIGIN,
    evaluate_simulation,
    generate_simulated_responses,
)


def registry() -> pd.DataFrame:
    return pd.read_csv("data/name_validation/name_candidates.csv")


def settings() -> dict[str, object]:
    return {
        "minimum_respondents": 100,
        "minimum_group_agreement": 0.70,
        "minimum_gender_agreement": 0.70,
        "minimum_median_confidence": 4.0,
        "maximum_between_group_ses_range": 0.75,
        "maximum_between_group_familiarity_range": 0.75,
        "maximum_between_group_unusual_range": 0.75,
    }


def test_simulated_panel_has_expected_shape():
    responses = generate_simulated_responses(registry())
    assert len(responses) == 960
    assert responses["respondent_id"].nunique() == 120
    valid = responses[responses["attention_check_passed"]]
    assert valid.groupby("candidate_id").size().eq(116).all()
    assert responses["data_origin"].eq(DATA_ORIGIN).all()


def test_simulation_exercises_thresholds_without_live_approval():
    responses = generate_simulated_responses(registry())
    summary, balance = evaluate_simulation(registry(), responses, settings())

    assert summary["passes_preregistered_thresholds_in_simulation"].all()
    assert not summary["approved_for_live_audit"].any()
    assert not summary["eligible_for_live_audit"].any()
    assert balance["pass"].all()
    assert not balance["eligible_for_live_audit"].any()


def test_simulated_paths_do_not_replace_production_survey():
    production = Path("data/name_validation/perception_responses.csv")
    simulated = Path(
        "data/simulated/name_validation/perception_responses_simulated.csv"
    )
    assert production != simulated
    assert "simulated" in simulated.parts
