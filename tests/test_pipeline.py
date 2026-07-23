from pathlib import Path

import numpy as np
import pytest

from compas_audit.analyze import (
    build_placebo_recovery,
    coefficient_frame,
    fit_cluster_models,
    prepare_data,
)
from compas_audit.common import extract_json_object, load_config
from compas_audit.generate import generate_permutations
from compas_audit.name_validation import assert_live_name_signals_validated
from compas_audit.providers import MockProvider
from compas_audit.run_audit import run_experiment, validate_result


def test_expanded_factorial_generation():
    frame = generate_permutations("config/audit.yaml", "data/templates/resume_templates.csv")
    assert len(frame) == 512
    assert frame["resume_id"].is_unique
    assert frame["matched_set_id"].nunique() == 32
    assert frame["occupation_id"].nunique() == 8
    assert set(frame["occupation_tier"]) == {"frontline", "knowledge"}
    assert frame.groupby("matched_set_id").size().eq(16).all()
    assert frame.groupby("occupation_id").size().eq(64).all()


def test_names_rotate_without_adding_a_gender_treatment():
    frame = generate_permutations("config/audit.yaml", "data/templates/resume_templates.csv")
    assert frame.groupby("signal_group")["candidate_name"].nunique().eq(2).all()
    assert frame["candidate_name"].str.split().str.len().eq(2).all()


def test_matched_resumes_differ_only_in_treatments():
    frame = generate_permutations("config/audit.yaml", "data/templates/resume_templates.csv")
    assert frame.groupby("matched_set_id")["qualification_hash"].nunique().max() == 1
    assert frame.groupby("matched_set_id")["years_experience"].nunique().max() == 1
    assert frame.groupby("matched_set_id")["target_role"].nunique().max() == 1
    assert frame.groupby("matched_set_id")["resume_word_count"].nunique().max() == 1


def test_balanced_treatment_allocation():
    frame = generate_permutations("config/audit.yaml", "data/templates/resume_templates.csv")
    cells = frame.groupby(
        ["signal_group", "education_pathway", "career_gap_months"]
    ).size()
    assert cells.nunique() == 1


def test_extract_and_validate_result():
    parsed = extract_json_object(
        '```json\n{"fit_score": 8, "recommend": true, "confidence": 0.8, '
        '"strengths": ["Relevant experience"], "risk_factors": [], '
        '"reason": "Good match."}\n```'
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
    prompt = "Candidate: Jamal Reed\nTarget role: Production Operations Supervisor\n"
    first = provider.screen("system", prompt, 0.0, 500, run_key="trial=1")
    repeat = provider.screen("system", prompt, 0.0, 500, run_key="trial=1")
    second_trial = provider.screen("system", prompt, 0.0, 500, run_key="trial=2")
    assert first == repeat
    assert first != second_trial


@pytest.fixture(scope="module")
def mock_results():
    resumes = generate_permutations("config/audit.yaml", "data/templates/resume_templates.csv")
    output = Path("outputs/resume_permutations.csv")
    output.parent.mkdir(exist_ok=True)
    resumes.to_csv(output, index=False)
    return run_experiment("config/audit.yaml", "mock")


def test_trial_count_metadata_and_raw_responses(mock_results):
    results = mock_results
    assert len(results) == 2560
    assert results["observation_id"].is_unique
    assert results.groupby("resume_id").size().eq(5).all()
    assert results["exact_model_id"].eq("mock-auditor-v3").all()
    assert results["prompt_version"].eq("v1.0-locked").all()
    assert results["raw_response"].fillna("").ne("").all()
    assert results["parser_status"].eq("parsed").all()


def test_clustered_model_recovers_planted_effects(mock_results):
    data = prepare_data(mock_results)
    fit_model, _ = fit_cluster_models(data)
    coefficients = coefficient_frame(fit_model, "fit_score")
    recovery = build_placebo_recovery(coefficients)
    effects = recovery.set_index("term")
    assert effects.loc["signal_a", "estimate"] == pytest.approx(-0.20, abs=0.03)
    assert effects.loc["signal_c", "estimate"] == pytest.approx(-0.35, abs=0.03)
    assert effects.loc["signal_c_frontline", "estimate"] == pytest.approx(-0.20, abs=0.04)
    assert effects.loc["has_gap", "estimate"] == pytest.approx(-0.45, abs=0.03)
    assert effects.loc["nontraditional", "estimate"] == pytest.approx(-0.15, abs=0.03)


def test_live_run_stops_when_names_are_unvalidated(tmp_path: Path):
    config = load_config("config/audit.yaml")
    config["name_validation"]["summary_output"] = str(tmp_path / "missing.csv")
    with pytest.raises(RuntimeError, match="validated perceived name signals"):
        assert_live_name_signals_validated(config)


def test_no_duplicate_qualification_hashes_within_set():
    frame = generate_permutations("config/audit.yaml", "data/templates/resume_templates.csv")
    counts = frame.groupby("matched_set_id")["qualification_hash"].nunique()
    assert np.all(counts.to_numpy() == 1)
