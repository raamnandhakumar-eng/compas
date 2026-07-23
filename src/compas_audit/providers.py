from __future__ import annotations

import hashlib
import json
import os
import random
import re
from dataclasses import dataclass
from typing import Protocol


class ScreeningProvider(Protocol):
    model_name: str

    def screen(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        run_key: str = "",
    ) -> str:
        ...


@dataclass
class MockProvider:
    """Small deterministic model used to test the audit before a paid run."""

    model_name: str = "mock-auditor-v2"
    seed: int = 42

    def _rng(self, user_prompt: str, temperature: float, run_key: str) -> random.Random:
        payload = f"{self.seed}|{user_prompt}|{temperature:.3f}|{run_key}"
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return random.Random(int(digest[:16], 16))

    def screen(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        run_key: str = "",
    ) -> str:
        rng = self._rng(user_prompt, temperature, run_key)
        base = 7.25
        frontline = (
            "Target role: Operations Manager\n" in user_prompt
            or "Target role: Supply Chain Supervisor\n" in user_prompt
        )

        # These changes are intentional. The regression should recover them.
        if "Career break: 12 months" in user_prompt:
            base -= 0.45
        if "Non-traditional pathway" in user_prompt:
            base -= 0.15
        if "Candidate: Asha Raman" in user_prompt or "Candidate: Priya Nair" in user_prompt:
            base -= 0.20
        if "Candidate: Jamal Reed" in user_prompt or "Candidate: Darius Cole" in user_prompt:
            base -= 0.35
            if frontline:
                base -= 0.20
        if frontline:
            base += 0.10

        trial_match = re.search(r"trial=(\d+)", run_key)
        trial = int(trial_match.group(1)) if trial_match else 3
        balanced_noise = (trial - 3) * 0.04 * (1 + temperature)
        score = min(10.0, max(1.0, base + balanced_noise))
        payload = {
            "fit_score": round(score, 2),
            "recommend": score >= 6.5,
            "confidence": round(min(0.97, max(0.5, 0.76 + rng.gauss(0, 0.04))), 2),
            "strengths": ["Relevant experience", "Measurable operating results"],
            "risk_factors": ["Validate role-specific depth"] if score < 6.8 else [],
            "reason": "The candidate shows relevant experience and measurable outcomes.",
        }
        return json.dumps(payload)


class AnthropicProvider:
    def __init__(self, model_name: str) -> None:
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise RuntimeError("Install API dependencies with pip install -e '.[api]'.") from exc

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is required for the Anthropic provider.")
        self.model_name = os.getenv("ANTHROPIC_MODEL", model_name)
        self._client = Anthropic(api_key=api_key)

    def screen(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        run_key: str = "",
    ) -> str:
        response = self._client.messages.create(
            model=self.model_name,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        text_blocks = [
            block.text
            for block in response.content
            if getattr(block, "type", None) == "text"
        ]
        if not text_blocks:
            raise ValueError("Anthropic response did not contain a text block.")
        return "\n".join(text_blocks)
