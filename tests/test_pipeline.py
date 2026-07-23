from pathlib import Path

import pytest

from compas_audit.analyze import (
    build_placebo_recovery,
    coefficient_frame,
    fit_cluster_models,
    prepare_data,
)
from compas_audit.common import extract_json_object
from compas_audit.generate import generate_permutations
from compas_audit.providers import MockProvider
from compas_audit.run_audit import run_experiment, validate_result


def test_complete_factorial_generation():
    frame = generate_permutations("config/audit.yaml", "data/templates/resume_templates.csv")
    assert len(frame) == 128
    assert frame["resume_id"].is_unique
    assert set(frame["occupation_tier"]) == {"frontline", "knowledge"}
    assert frame.groupby("template_id").size().nunique() == 1
    assert frame["onet_soc_code"].notna().all()


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
        validate_result(
            {
                "fit_score": 11,
                "recommend": True,
                "confidence": 0.8,
                "strengths": [],
                "risk_factors": [],
                "reason": "Invalid.",
            }
        )


def test_mock_provider_is_stable_and_trial_sensitive():
    provider = MockProvider(seed=42)
    prompt = "Candidate: Jamal Reed\nTarget role: Operations Manager"
    first = provider.screen("system", prompt, 0.4, 500, run_key="trial=1")
    repeat = provider.screen("system", prompt, 0.4, 500, run_key="trial=1")
    second_trial = provider.screen("system", prompt, 0.4, 500, run_key="trial=2")
    assert first == repeat
    assert first != second_trial


def test_clustered_model_recovers_planted_effects(tmp_path: Path):
    resumes = generate_permutations("config/audit.yaml", "data/templates/resume_templates.csv")
    output = Path("outputs/resume_permutations.csv")
    output.parent.mkdir(exist_ok=True)
    resumes.to_csv(output, index=False)
    results = run_experiment("config/audit.yaml", "mock")
    data = prepare_data(results)
    fit_model, _ = fit_cluster_models(data)
    coefficients = coefficient_frame(fit_model, "fit_score")
    recovery = build_placebo_recovery(coefficients)
    effects = recovery.set_index("term")
    assert effects.loc["signal_c", "estimate"] == pytest.approx(-0.35, abs=0.10)
    assert effects.loc["signal_c_frontline", "estimate"] == pytest.approx(-0.20, abs=0.12)
    assert effects.loc["has_gap", "estimate"] == pytest.approx(-0.45, abs=0.08)
    assert effects.loc["nontraditional", "estimate"] == pytest.approx(-0.15, abs=0.08)
