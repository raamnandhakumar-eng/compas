from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pandas as pd

from .common import extract_json_object, load_config, sha256_text, stable_id
from .name_validation import assert_live_name_signals_validated
from .prompts import SYSTEM_PROMPT, screening_prompt
from .providers import AnthropicProvider, MockProvider, ScreeningProvider

REQUIRED_KEYS = {"fit_score", "recommend", "confidence", "strengths", "risk_factors", "reason"}
REFUSAL_PHRASES = (
    "cannot assist",
    "can't assist",
    "cannot evaluate",
    "unable to evaluate",
    "cannot make hiring",
)


def validate_result(payload: dict[str, Any]) -> dict[str, Any]:
    missing = REQUIRED_KEYS - payload.keys()
    if missing:
        raise ValueError(f"Missing response fields: {sorted(missing)}")

    fit_score = float(payload["fit_score"])
    confidence = float(payload["confidence"])
    if not 1 <= fit_score <= 10:
        raise ValueError("fit_score must be between 1 and 10.")
    if not 0 <= confidence <= 1:
        raise ValueError("confidence must be between 0 and 1.")
    if not isinstance(payload["recommend"], bool):
        raise ValueError("recommend must be a boolean.")
    if not isinstance(payload["strengths"], list) or not isinstance(payload["risk_factors"], list):
        raise ValueError("strengths and risk_factors must be lists.")

    return {
        "fit_score": fit_score,
        "recommend": int(payload["recommend"]),
        "confidence": confidence,
        "strengths": json.dumps(payload["strengths"], ensure_ascii=False),
        "risk_factors": json.dumps(payload["risk_factors"], ensure_ascii=False),
        "reason": str(payload["reason"]),
    }


def assert_external_preregistration(config: dict[str, Any]) -> str:
    settings = config.get("external_preregistration", {})
    if not bool(settings.get("required_for_live", False)):
        return ""

    env_var = str(settings.get("url_env_var", "EXTERNAL_PREREGISTRATION_URL"))
    registration_url = os.getenv(env_var, "").strip()
    source_document = str(settings.get("source_document", "docs/osf_preregistration.md"))
    if not registration_url:
        raise RuntimeError(
            f"A public OSF or AsPredicted preregistration is required before a live run. "
            f"Submit {source_document}, then set {env_var} to its permanent URL."
        )

    parsed = urlparse(registration_url)
    hostname = (parsed.hostname or "").casefold()
    accepted_hosts = [
        str(value).casefold()
        for value in settings.get("accepted_hosts", ["osf.io", "aspredicted.org"])
    ]
    host_is_allowed = any(
        hostname == allowed or hostname.endswith(f".{allowed}") for allowed in accepted_hosts
    )
    if parsed.scheme != "https" or not host_is_allowed:
        allowed_text = ", ".join(accepted_hosts)
        raise RuntimeError(
            f"{env_var} must be a permanent HTTPS registration URL hosted by: {allowed_text}."
        )
    return registration_url


def build_provider(name: str, model: str, seed: int) -> ScreeningProvider:
    if name == "mock":
        return MockProvider(seed=seed)
    if name == "anthropic":
        return AnthropicProvider(model_name=model)
    raise ValueError(f"Unknown provider: {name}")


def _looks_like_refusal(raw_response: str) -> bool:
    lowered = raw_response.casefold()
    return any(phrase in lowered for phrase in REFUSAL_PHRASES)


def run_experiment(config_path: str, provider_name: str, limit: int | None = None) -> pd.DataFrame:
    config = load_config(config_path)
    external_preregistration_url = ""
    if provider_name == "anthropic":
        external_preregistration_url = assert_external_preregistration(config)
        assert_live_name_signals_validated(config)

    resumes_path = Path(config.get("output_resumes", "outputs/resume_permutations.csv"))
    if not resumes_path.exists():
        raise FileNotFoundError(
            f"Resume permutations not found: {resumes_path}. Run hiring-audit-generate first."
        )

    seed = int(config.get("seed", 42))
    resumes = pd.read_csv(resumes_path).sample(frac=1, random_state=seed).reset_index(drop=True)
    if limit is not None:
        resumes = resumes.head(limit)

    provider_cfg = config.get("provider", {})
    provider = build_provider(
        provider_name,
        str(provider_cfg.get("model", "set-via-ANTHROPIC_MODEL-before-live-run")),
        seed,
    )
    trials = int(config.get("trials_per_resume", 1))
    temperatures = [float(value) for value in config.get("temperatures", [0.0])]
    max_tokens = int(provider_cfg.get("max_tokens", 500))
    delay = float(provider_cfg.get("request_delay_seconds", 0.0))
    api_version = str(provider_cfg.get("api_version", "unknown"))
    prompt_version = str(provider_cfg.get("prompt_version", "unknown"))

    jobs: list[tuple[pd.Series, float, int]] = []
    for _, resume in resumes.iterrows():
        for temperature in temperatures:
            for trial in range(1, trials + 1):
                jobs.append((resume, temperature, trial))
    random_order = pd.Series(range(len(jobs))).sample(frac=1, random_state=seed + 1).tolist()

    records: list[dict[str, Any]] = []
    for execution_order, job_index in enumerate(random_order, start=1):
        resume, temperature, trial = jobs[job_index]
        user_prompt = screening_prompt(str(resume["target_role"]), str(resume["resume_text"]))
        observation_id = stable_id(
            resume["resume_id"],
            provider.model_name,
            temperature,
            trial,
        )
        started = time.perf_counter()
        timestamp = datetime.now(timezone.utc)
        raw_response = ""
        error = ""
        error_type = ""
        parser_status = "not_attempted"
        parsed: dict[str, Any] = {}
        try:
            raw_response = provider.screen(
                SYSTEM_PROMPT,
                user_prompt,
                temperature,
                max_tokens,
                run_key=f"{observation_id}|trial={trial}",
            )
            parsed = validate_result(extract_json_object(raw_response))
            parser_status = "parsed"
        except Exception as exc:
            error_type = type(exc).__name__
            error = f"{error_type}: {exc}"
            parser_status = "error"

        records.append(
            {
                **resume.to_dict(),
                "observation_id": observation_id,
                "run_id": observation_id,
                "execution_order": execution_order,
                "provider": provider_name,
                "exact_model_id": provider.model_name,
                "model": provider.model_name,
                "api_version": api_version,
                "run_date": timestamp.date().isoformat(),
                "timestamp_utc": timestamp.isoformat(),
                "temperature": temperature,
                "prompt_version": prompt_version,
                "external_preregistration_url": external_preregistration_url,
                "system_prompt": SYSTEM_PROMPT,
                "user_prompt": user_prompt,
                "trial_number": trial,
                "trial": trial,
                "latency_seconds": round(time.perf_counter() - started, 4),
                "prompt_sha256": sha256_text(SYSTEM_PROMPT + "\n" + user_prompt),
                **parsed,
                "response_length_chars": len(raw_response),
                "refusal": int(_looks_like_refusal(raw_response)),
                "raw_response": raw_response,
                "parser_status": parser_status,
                "error_type": error_type,
                "error": error,
            }
        )
        if delay > 0:
            time.sleep(delay)

    results = (
        pd.DataFrame.from_records(records)
        .sort_values("execution_order")
        .reset_index(drop=True)
    )
    if results["observation_id"].duplicated().any():
        raise RuntimeError("Duplicate observation IDs were generated.")
    return results


def write_manifest(config_path: str, results: pd.DataFrame, output_path: Path) -> None:
    config_text = Path(config_path).read_text(encoding="utf-8")
    successful = int(results["error"].fillna("").eq("").sum())
    preregistration_url = (
        str(results["external_preregistration_url"].iloc[0])
        if not results.empty and "external_preregistration_url" in results
        else ""
    )
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "config_sha256": sha256_text(config_text),
        "provider": str(results["provider"].iloc[0]) if not results.empty else None,
        "exact_model_id": str(results["exact_model_id"].iloc[0]) if not results.empty else None,
        "api_version": str(results["api_version"].iloc[0]) if not results.empty else None,
        "prompt_version": str(results["prompt_version"].iloc[0]) if not results.empty else None,
        "external_preregistration_url": preregistration_url,
        "externally_preregistered": bool(preregistration_url),
        "rows": int(len(results)),
        "successful_rows": successful,
        "failed_rows": int(len(results) - successful),
        "refusals": int(results["refusal"].sum()) if not results.empty else 0,
        "unique_resumes": int(results["resume_id"].nunique()) if not results.empty else 0,
        "unique_occupations": int(results["occupation_id"].nunique()) if not results.empty else 0,
        "temperatures": (
            sorted(results["temperature"].dropna().unique().tolist())
            if not results.empty
            else []
        ),
        "trials": (
            sorted(results["trial_number"].dropna().unique().tolist())
            if not results.empty
            else []
        ),
        "randomized_execution_order": True,
        "selective_reruns_permitted": False,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the synthetic LLM hiring audit.")
    parser.add_argument("--config", default="config/audit.yaml")
    parser.add_argument("--provider", choices=["mock", "anthropic"], default="mock")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional number of resumes for a smoke test. Do not use for the confirmatory run.",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    output = Path(config.get("output_results", "outputs/screening_results.csv"))
    manifest_path = Path(config.get("output_manifest", "outputs/run_manifest.json"))
    output.parent.mkdir(parents=True, exist_ok=True)
    results = run_experiment(args.config, args.provider, limit=args.limit)
    results.to_csv(output, index=False)
    write_manifest(args.config, results, manifest_path)
    successful = int(results["error"].fillna("").eq("").sum())
    print(f"Wrote {len(results)} trials to {output}; successful={successful}")


if __name__ == "__main__":
    main()
