import pytest

from compas_audit.common import extract_json_object
from compas_audit.generate import generate_permutations
from compas_audit.run_audit import validate_result


def test_complete_factorial_generation():
    frame = generate_permutations("config/audit.yaml", "data/templates/resume_templates.csv")
    assert len(frame) == 128
    assert frame["resume_id"].is_unique
    assert set(frame["occupation_tier"]) == {"frontline", "knowledge"}
    assert frame.groupby("template_id").size().nunique() == 1


def test_qualifications_are_matched_within_template():
    frame = generate_permutations("config/audit.yaml", "data/templates/resume_templates.csv")
    assert frame.groupby("template_id")["years_experience"].nunique().max() == 1
    assert frame.groupby("template_id")["target_role"].nunique().max() == 1


def test_extract_and_validate_result():
    parsed = extract_json_object(
        '```json\n{"fit_score": 8, "recommend": true, "confidence": 0.8, '
        '"strengths": ["Relevant experience"], "risk_factors": [], "reason": "Good match."}\n```'
    )
    result = validate_result(parsed)
    assert result["fit_score"] == 8
    assert result["recommend"] == 1


def test_invalid_score_is_rejected():
    with pytest.raises(ValueError):
        validate_result({
            "fit_score": 11,
            "recommend": True,
            "confidence": 0.8,
            "strengths": [],
            "risk_factors": [],
            "reason": "Invalid.",
        })
