from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass
from typing import Protocol


class ScreeningProvider(Protocol):
    model_name: str

    def screen(self, system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> str:
        ...


@dataclass
class MockProvider:
    """Deterministic provider for tests and end-to-end demonstrations."""

    model_name: str = "mock-auditor-v1"
    seed: int = 42

    def screen(self, system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> str:
        local_seed = hash((self.seed, user_prompt, round(temperature, 3))) & 0xFFFFFFFF
        rng = random.Random(local_seed)
        base = 7.0
        if "Career break: 12 months" in user_prompt:
            base -= 0.45
        if "Non-traditional pathway" in user_prompt:
            base -= 0.15
        if "Operations Manager" in user_prompt or "Supply Chain Supervisor" in user_prompt:
            base += 0.1
        score = min(10.0, max(1.0, base + rng.uniform(-0.2, 0.2) * (1 + temperature)))
        payload = {
            "fit_score": round(score, 2),
            "recommend": score >= 6.5,
            "confidence": round(min(0.95, 0.72 + rng.uniform(-0.04, 0.04)), 2),
            "strengths": ["Relevant experience", "Measurable operating results"],
            "risk_factors": ["Validate role-specific depth"] if score < 7.2 else [],
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

    def screen(self, system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> str:
        response = self._client.messages.create(
            model=self.model_name,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        text_blocks = [block.text for block in response.content if getattr(block, "type", None) == "text"]
        if not text_blocks:
            raise ValueError("Anthropic response did not contain a text block.")
        return "\n".join(text_blocks)
