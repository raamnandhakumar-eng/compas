#!/usr/bin/env python3
"""Pre-run analytic power calculations for the matched audit design."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import pandas as pd
from scipy.stats import norm


def minimum_detectable_effect(
    clusters: int,
    paired_standard_deviation: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> float:
    critical = norm.ppf(1 - alpha / 2) + norm.ppf(power)
    return float(critical * paired_standard_deviation / math.sqrt(clusters))


def required_trials(
    clusters: int,
    single_call_standard_deviation: float,
    target_effect: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> int:
    critical = norm.ppf(1 - alpha / 2) + norm.ppf(power)
    required = (
        critical * single_call_standard_deviation / target_effect
    ) ** 2 / clusters
    return max(1, math.ceil(required))


def build_power_table(clusters: int, trials: int) -> pd.DataFrame:
    assumptions = [
        {
            "outcome": "fit_score",
            "paired_standard_deviation_after_repeats": 0.60,
            "single_call_standard_deviation": 0.90,
            "target_effect": 0.30,
        },
        {
            "outcome": "recommendation_rate",
            "paired_standard_deviation_after_repeats": 0.35,
            "single_call_standard_deviation": 0.50,
            "target_effect": 0.15,
        },
    ]
    rows = []
    for item in assumptions:
        rows.append(
            {
                **item,
                "matched_sets": clusters,
                "planned_trials": trials,
                "alpha_two_sided": 0.05,
                "power": 0.80,
                "minimum_detectable_effect": minimum_detectable_effect(
                    clusters,
                    item["paired_standard_deviation_after_repeats"],
                ),
                "minimum_trials_for_target_effect": required_trials(
                    clusters,
                    item["single_call_standard_deviation"],
                    item["target_effect"],
                ),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run preregistered audit power calculations.")
    parser.add_argument("--matched-sets", type=int, default=32)
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--output", default="outputs/power_analysis.csv")
    args = parser.parse_args()

    table = build_power_table(args.matched_sets, args.trials)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(output, index=False)
    print(table.to_string(index=False))
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
