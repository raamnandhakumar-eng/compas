from __future__ import annotations

import argparse
import itertools
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {
    "candidate_id",
    "signal_group",
    "full_name",
    "valid_respondents",
    "group_agreement",
    "gender_agreement",
    "median_confidence",
    "mean_familiarity",
    "mean_socioeconomic_status",
    "mean_unusual",
}
BALANCE_METRICS = (
    "mean_familiarity",
    "mean_socioeconomic_status",
    "mean_unusual",
)


def eligible_candidates(
    candidates: pd.DataFrame,
    minimum_respondents: int = 30,
    minimum_group_agreement: float = 0.70,
    minimum_gender_agreement: float = 0.70,
    minimum_median_confidence: float = 4.0,
) -> pd.DataFrame:
    missing = REQUIRED_COLUMNS - set(candidates.columns)
    if missing:
        raise ValueError(f"Candidate summary is missing columns: {sorted(missing)}")

    data = candidates.copy()
    numeric = [
        "valid_respondents",
        "group_agreement",
        "gender_agreement",
        "median_confidence",
        *BALANCE_METRICS,
    ]
    for column in numeric:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    complete = data[numeric].notna().all(axis=1)
    return data[
        complete
        & data["valid_respondents"].ge(minimum_respondents)
        & data["group_agreement"].ge(minimum_group_agreement)
        & data["gender_agreement"].ge(minimum_gender_agreement)
        & data["median_confidence"].ge(minimum_median_confidence)
    ].copy()


def panel_diagnostics(panel: pd.DataFrame, maximum_range: float = 0.75) -> pd.DataFrame:
    group_means = panel.groupby("signal_group")[list(BALANCE_METRICS)].mean()
    rows = []
    for metric in BALANCE_METRICS:
        observed_range = float(group_means[metric].max() - group_means[metric].min())
        rows.append(
            {
                "metric": metric,
                "between_group_range": observed_range,
                "maximum_allowed": maximum_range,
                "pass": observed_range <= maximum_range,
            }
        )
    return pd.DataFrame(rows)


def _objective(panel: pd.DataFrame) -> tuple[float, float, float, str]:
    diagnostics = panel_diagnostics(panel, maximum_range=float("inf"))
    ranges = diagnostics["between_group_range"]
    mean_agreement = float(
        panel[["group_agreement", "gender_agreement"]].to_numpy().mean()
    )
    names = "|".join(sorted(panel["full_name"].astype(str)))
    return (
        float(ranges.max()),
        float(ranges.sum()),
        -mean_agreement,
        names,
    )


def select_balanced_panel(
    candidates: pd.DataFrame,
    names_per_group: int = 2,
    maximum_range: float = 0.75,
    minimum_respondents: int = 30,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    eligible = eligible_candidates(
        candidates,
        minimum_respondents=minimum_respondents,
    )
    groups = sorted(candidates["signal_group"].dropna().astype(str).unique())
    if not groups:
        raise ValueError("No signal groups were found.")

    group_options: list[list[tuple[int, ...]]] = []
    for group in groups:
        indices = eligible.index[eligible["signal_group"].astype(str).eq(group)].tolist()
        if len(indices) < names_per_group:
            raise ValueError(
                f"{group} has {len(indices)} eligible candidates; "
                f"{names_per_group} are required."
            )
        group_options.append(list(itertools.combinations(indices, names_per_group)))

    best_panel: pd.DataFrame | None = None
    best_objective: tuple[float, float, float, str] | None = None
    for combination in itertools.product(*group_options):
        flat_indices = [index for group_choice in combination for index in group_choice]
        panel = eligible.loc[flat_indices].copy()
        objective = _objective(panel)
        if best_objective is None or objective < best_objective:
            best_panel = panel
            best_objective = objective

    if best_panel is None:
        raise RuntimeError("No candidate panel could be constructed.")

    diagnostics = panel_diagnostics(best_panel, maximum_range=maximum_range)
    diagnostics["panel_pass"] = bool(diagnostics["pass"].all())
    best_panel = best_panel.sort_values(["signal_group", "full_name"]).reset_index(drop=True)
    return best_panel, diagnostics


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Select a balanced perceived-name panel from pilot summaries."
    )
    parser.add_argument("--input", required=True)
    parser.add_argument(
        "--selected-output",
        default="results/name_validation/replacement_panel_selected.csv",
    )
    parser.add_argument(
        "--diagnostics-output",
        default="results/name_validation/replacement_panel_diagnostics.csv",
    )
    parser.add_argument("--names-per-group", type=int, default=2)
    parser.add_argument("--maximum-range", type=float, default=0.75)
    parser.add_argument("--minimum-respondents", type=int, default=30)
    args = parser.parse_args()

    candidates = pd.read_csv(args.input)
    selected, diagnostics = select_balanced_panel(
        candidates,
        names_per_group=args.names_per_group,
        maximum_range=args.maximum_range,
        minimum_respondents=args.minimum_respondents,
    )

    selected_path = Path(args.selected_output)
    diagnostics_path = Path(args.diagnostics_output)
    selected_path.parent.mkdir(parents=True, exist_ok=True)
    diagnostics_path.parent.mkdir(parents=True, exist_ok=True)
    selected.to_csv(selected_path, index=False)
    diagnostics.to_csv(diagnostics_path, index=False)

    if not diagnostics["pass"].all():
        raise SystemExit(
            "Best available panel does not satisfy every locked balance threshold. "
            "Expand the candidate pool and rerun the pilot."
        )

    print(
        f"Selected {len(selected)} names across "
        f"{selected['signal_group'].nunique()} groups."
    )


if __name__ == "__main__":
    main()
