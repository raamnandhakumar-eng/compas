import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


NONZERO_TERMS = {
    "has_gap": "12-month career gap",
    "nontraditional": "Non-traditional education",
    "signal_a": "Signal A",
    "signal_c": "Signal C",
    "signal_c_frontline": "Signal C × frontline",
}


def make_summary_figure(quality: pd.DataFrame, recovery: pd.DataFrame, output: Path) -> None:
    row = quality.iloc[0]
    mean_error = recovery["abs_recovery_error"].mean()
    metrics = [
        (f"{int(row['valid_rows']):,}", "successful evaluations"),
        (f"{int(row['failed_rows']):,}", "parser failures"),
        (f"{int(row['unique_resumes']):,}", "matched resumes"),
        (f"{mean_error:.3f}", "mean recovery error"),
    ]

    figure, axis = plt.subplots(figsize=(10, 3.2))
    axis.axis("off")
    axis.set_title("Completed placebo validation", fontsize=20, fontweight="bold", pad=18)

    for index, (value, label) in enumerate(metrics):
        x_position = 0.125 + index * 0.25
        axis.text(
            x_position,
            0.58,
            value,
            ha="center",
            va="center",
            fontsize=30,
            fontweight="bold",
            transform=axis.transAxes,
        )
        axis.text(
            x_position,
            0.32,
            label,
            ha="center",
            va="center",
            fontsize=11,
            transform=axis.transAxes,
        )

    axis.text(
        0.5,
        0.04,
        "These results validate the software and estimator, not Claude or real hiring systems.",
        ha="center",
        fontsize=9,
        transform=axis.transAxes,
    )
    figure.tight_layout()
    figure.savefig(output / "placebo_run_summary.svg", format="svg", bbox_inches="tight")
    plt.close(figure)


def make_recovery_figure(recovery: pd.DataFrame, output: Path) -> None:
    plotted = recovery[recovery["term"].isin(NONZERO_TERMS)].copy()
    plotted["label"] = plotted["term"].map(NONZERO_TERMS)
    plotted = plotted.set_index("label")[["expected_effect", "estimate"]]
    plotted.columns = ["Planted", "Recovered"]

    axis = plotted.plot(kind="barh", figsize=(10, 5))
    axis.axvline(0, linewidth=0.8)
    axis.set_xlabel("Change in fit score")
    axis.set_ylabel("")
    axis.set_title("Planted effects were recovered exactly")
    axis.invert_yaxis()
    axis.text(
        0.5,
        -0.18,
        "Placebo validation only. Mean absolute recovery error: 0.000 points.",
        ha="center",
        transform=axis.transAxes,
    )
    figure = axis.get_figure()
    figure.tight_layout()
    figure.savefig(output / "placebo_effect_recovery.svg", format="svg", bbox_inches="tight")
    plt.close(figure)


def make_group_score_figure(summary: pd.DataFrame, output: Path) -> None:
    pivot = summary.pivot(
        index="signal_group",
        columns="occupation_tier",
        values="mean_fit_score",
    )
    axis = pivot.plot(kind="bar", figsize=(9, 5))
    axis.set_xlabel("Experimental signal group")
    axis.set_ylabel("Mean fit score")
    axis.set_title("Mean fit scores in the completed placebo run")
    axis.set_ylim(6.3, 7.2)
    axis.tick_params(axis="x", rotation=0)
    axis.legend(title="Occupation tier")
    axis.text(
        0.5,
        -0.2,
        "Scores reflect planted test effects, not observed behavior from Claude.",
        ha="center",
        transform=axis.transAxes,
    )
    figure = axis.get_figure()
    figure.tight_layout()
    figure.savefig(output / "placebo_group_scores.svg", format="svg", bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build figures from committed placebo results.")
    parser.add_argument("--results", type=Path, default=Path("results/placebo"))
    parser.add_argument("--output", type=Path, default=Path("docs/figures"))
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    quality = pd.read_csv(args.results / "data_quality.csv")
    summary = pd.read_csv(args.results / "descriptive_summary.csv")
    recovery = pd.read_csv(args.results / "placebo_effect_recovery.csv")

    make_summary_figure(quality, recovery, args.output)
    make_recovery_figure(recovery, args.output)
    make_group_score_figure(summary, args.output)
    print(f"Wrote result figures to {args.output}")


if __name__ == "__main__":
    main()
