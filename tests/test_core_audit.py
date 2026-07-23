from pathlib import Path

import pandas as pd
import yaml

from compas_audit.core_analysis import (
    PRIMARY_TERMS,
    core_model_formula,
    failure_sensitivity,
    fit_core_logistic_recommendation,
    placebo_recovery,
    prepare_core_data,
)
from compas_audit.generate import generate_permutations


def test_core_config_generates_complete_matched_design():
    resumes = generate_permutations(
        "config/core_audit.yaml",
        "data/templates/resume_templates.csv",
    )
    assert len(resumes) == 128
    assert resumes["occupation_id"].nunique() == 8
    assert resumes["matched_set_id"].nunique() == 32
    assert resumes.groupby("matched_set_id").size().eq(4).all()
    assert resumes.groupby("matched_set_id")["candidate_name"].nunique().eq(1).all()
    assert resumes["signal_group"].eq("signal_control").all()


def test_core_live_run_does_not_require_name_pretest():
    config = yaml.safe_load(Path("config/core_audit.yaml").read_text(encoding="utf-8"))
    assert config["name_validation"]["required_for_live"] is False
    assert config["design"]["planned_resumes"] == 128
    assert config["design"]["planned_evaluations"] == 640


def test_core_formula_contains_only_preregistered_treatments():
    formula = core_model_formula("fit_score")
    assert "signal_a" not in formula
    assert "signal_b" not in formula
    assert "nontraditional" in formula
    assert "has_gap" in formula
    assert PRIMARY_TERMS == {
        "nontraditional",
        "has_gap",
        "nontraditional:frontline",
        "has_gap:frontline",
    }


def _prepared_frame(recommendations: tuple[int, int] = (1, 0)) -> pd.DataFrame:
    frame = pd.DataFrame(
        [
            {
                "occupation_tier": "frontline",
                "education_pathway": "traditional",
                "career_gap_months": 0,
                "resume_id": "r1",
                "matched_set_id": "m1",
                "occupation_id": "o1",
                "temperature": 0.0,
                "fit_score": 7,
                "recommend": recommendations[0],
                "confidence": 0.8,
                "error": "",
            },
            {
                "occupation_tier": "knowledge",
                "education_pathway": "nontraditional",
                "career_gap_months": 12,
                "resume_id": "r2",
                "matched_set_id": "m2",
                "occupation_id": "o2",
                "temperature": 0.0,
                "fit_score": 6,
                "recommend": recommendations[1],
                "confidence": 0.7,
                "error": "",
            },
        ]
    )
    return prepare_core_data(frame)


def test_core_data_preparation():
    prepared = _prepared_frame()
    assert prepared["frontline"].tolist() == [1, 0]
    assert prepared["nontraditional"].tolist() == [0, 1]
    assert prepared["has_gap"].tolist() == [0, 1]


def test_constant_recommendation_is_reported_not_estimable():
    prepared = _prepared_frame(recommendations=(1, 1))
    assert fit_core_logistic_recommendation(prepared) is None
    sensitivity = failure_sensitivity(prepared)
    assert sensitivity.empty


def test_core_placebo_recovery_uses_only_core_terms():
    coefficients = pd.DataFrame(
        [
            {
                "outcome": "fit_score",
                "model_type": "linear",
                "term": term,
                "estimate": value,
                "std_error_clustered": 0.01,
                "p_value": 0.01,
                "q_value_bh": 0.02,
                "ci_95_low": value - 0.02,
                "ci_95_high": value + 0.02,
            }
            for term, value in {
                "nontraditional": -0.15,
                "has_gap": -0.45,
                "nontraditional:frontline": 0.0,
                "has_gap:frontline": 0.0,
            }.items()
        ]
    )
    recovery = placebo_recovery(coefficients)
    assert recovery["abs_recovery_error"].eq(0).all()
