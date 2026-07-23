from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from .common import extract_json_object, load_config, sha256_text, stable_id
from .prompts import SYSTEM_PROMPT, screening_prompt
from .providers import AnthropicProvider, MockProvider, ScreeningProvider

REQUIRED_KEYS = {"fit_score", "recommend", "confidence", "strengths", "risk_factors", "reason"}


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


def build_provider(name: str, model: str, seed: int) -> ScreeningProvider:
    if name == "mock":
        return MockProvider(seed=seed)
    if name == "anthropic":
        return AnthropicProvider(model_name=model)
    raise ValueError(f"Unknown provider: {name}")


def run_experiment(config_path: str, provider_name: str, limit: int | None = None) -> pd.DataFrame:
    config = load_config(config_path)
    resumes_path = Path(config.get("output_resumes", "outputs/resume_permutations.csv"))
    if not resumes_path.exists():
        raise FileNotFoundError(
            f"Resume permutations not found: {resumes_path}. "
            "Run compas-generate first."
        )

    seed = int(config.get("seed", 42))
    resumes = pd.read_csv(resumes_path).sample(frac=1, random_state=seed).reset_index(drop=True)
    if limit is not None:
        resumes = resumes.head(limit)

    provider_cfg = config.get("provider", {})
    provider = build_provider(
        provider_name,
        str(provider_cfg.get("model", "claude-sonnet-4-20250514")),
        seed,
    )
    trials = int(config.get("trials_per_resume", 1))
    temperatures = [float(value) for value in config.get("temperatures", [0.0])]
    max_tokens = int(provider_cfg.get("max_tokens", 500))
    delay = float(provider_cfg.get("request_delay_seconds", 0.0))

    jobs: list[tuple[pd.Series, float, int]] = []
    for _, resume in resumes.iterrows():
        for temperature in temperatures:
            for trial in range(1, trials + 1):
                jobs.append((resume, temperature, trial))
    random_order = pd.Series(range(len(jobs))).sample(frac=1, random_state=seed + 1).tolist()

    records: list[dict[str, Any]] = []
    for execution_order, job_index in enumerate(random_order, start=1):
        resume, temperature, trial = jobs[job_index]
        prompt = screening_prompt(str(resume["target_role"]), str(resume["resume_text"]))
        run_id = stable_id(resume["resume_id"], provider.model_name, temperature, trial)
        started = time.perf_counter()
        raw_response = ""
        error = ""
        parsed: dict[str, Any] = {}
        try:
            raw_response = provider.screen(
                SYSTEM_PROMPT,
                prompt,
                temperature,
                max_tokens,
                run_key=f"{run_id}|trial={trial}",
            )
            parsed = validate_result(extract_json_object(raw_response))
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"

        records.append(
            {
                **resume.to_dict(),
                "run_id": run_id,
                "execution_order": execution_order,
                "provider": provider_name,
                "model": provider.model_name,
                "temperature": temperature,
                "trial": trial,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "latency_seconds": round(time.perf_counter() - started, 4),
                "prompt_sha256": sha256_text(SYSTEM_PROMPT + "\n" + prompt),
                **parsed,
                "raw_response": raw_response,
                "error": error,
            }
        )
        if delay > 0:
            time.sleep(delay)

    return pd.DataFrame.from_records(records).sort_values("execution_order").reset_index(drop=True)


def write_manifest(config_path: str, results: pd.DataFrame, output_path: Path) -> None:
    config_text = Path(config_path).read_text(encoding="utf-8")
    successful = int(results["error"].fillna("").eq("").sum())
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "config_sha256": sha256_text(config_text),
        "provider": str(results["provider"].iloc[0]) if not results.empty else None,
        "model": str(results["model"].iloc[0]) if not results.empty else None,
        "rows": int(len(results)),
        "successful_rows": successful,
        "failed_rows": int(len(results) - successful),
        "unique_resumes": int(results["resume_id"].nunique()) if not results.empty else 0,
        "temperatures": (
            sorted(results["temperature"].dropna().unique().tolist())
            if not results.empty
            else []
        ),
        "trials": sorted(results["trial"].dropna().unique().tolist()) if not results.empty else [],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the synthetic LLM screening audit.")
    parser.add_argument("--config", default="config/audit.yaml")
    parser.add_argument("--provider", choices=["mock", "anthropic"], default="mock")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional number of resumes for a smoke test.",
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
