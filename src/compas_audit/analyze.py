from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.formula.api as smf


def prepare_data(frame: pd.DataFrame) -> pd.DataFrame:
    required = {
        "fit_score", "recommend", "signal_group", "occupation_tier",
        "education_pathway", "career_gap_months", "template_id", "resume_id",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Input is missing required columns: {sorted(missing)}")

    data = frame.copy()
    if "error" in data:
        data = data[data["error"].fillna("").eq("")]
    data["frontline"] = (data["occupation_tier"] == "frontline").astype(int)
    data["nontraditional"] = (data["education_pathway"] == "nontraditional").astype(int)
    data["has_gap"] = (pd.to_numeric(data["career_gap_months"]) > 0).astype(int)
    data["fit_score"] = pd.to_numeric(data["fit_score"], errors="coerce")
    data["recommend"] = pd.to_numeric(data["recommend"], errors="coerce")
    data = data.dropna(subset=["fit_score", "recommend"])
    if data.empty:
        raise ValueError("No valid audit rows remain after filtering failures.")
    return data


def fit_hc1_models(data: pd.DataFrame):
    formula = (
        "{outcome} ~ C(signal_group) * frontline + nontraditional * frontline "
        "+ has_gap * frontline + C(template_id) + C(temperature)"
    )
    fit_model = smf.ols(formula.format(outcome="fit_score"), data=data).fit(cov_type="HC1")
    rec_model = smf.ols(formula.format(outcome="recommend"), data=data).fit(cov_type="HC1")
    return fit_model, rec_model


def coefficient_frame(model, outcome: str) -> pd.DataFrame:
    intervals = model.conf_int()
    return pd.DataFrame({
        "outcome": outcome,
        "term": model.params.index,
        "estimate": model.params.values,
        "std_error_hc1": model.bse.values,
        "p_value": model.pvalues.values,
        "ci_95_low": intervals[0].values,
        "ci_95_high": intervals[1].values,
    })


def save_bar_plot(summary: pd.DataFrame, value: str, ylabel: str, path: Path) -> None:
    pivot = summary.pivot(index="signal_group", columns="occupation_tier", values=value)
    ax = pivot.plot(kind="bar")
    ax.set_xlabel("Experimental signal group")
    ax.set_ylabel(ylabel)
    ax.set_title(f"{ylabel} by signal group and occupational tier")
    ax.legend(title="Occupational tier")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def analyze(input_path: str, output_dir: str) -> None:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    data = prepare_data(pd.read_csv(input_path))

    summary = data.groupby(["signal_group", "occupation_tier"], as_index=False).agg(
        mean_fit_score=("fit_score", "mean"),
        recommendation_rate=("recommend", "mean"),
        mean_confidence=("confidence", "mean"),
        observations=("run_id", "count"),
    )
    summary.to_csv(output / "descriptive_summary.csv", index=False)

    reference = summary.groupby("occupation_tier")["mean_fit_score"].transform("max")
    summary.assign(fit_gap_from_tier_max=summary["mean_fit_score"] - reference).to_csv(
        output / "group_disparities.csv", index=False
    )

    stability = data.groupby(["resume_id", "temperature"], as_index=False).agg(
        mean_fit_score=("fit_score", "mean"),
        fit_score_sd=("fit_score", "std"),
        recommendation_rate=("recommend", "mean"),
        trials=("trial", "count"),
    )
    stability.to_csv(output / "trial_stability.csv", index=False)

    fit_model, rec_model = fit_hc1_models(data)
    (output / "ols_fit_score_hc1.txt").write_text(fit_model.summary().as_text(), encoding="utf-8")
    (output / "ols_recommendation_hc1.txt").write_text(rec_model.summary().as_text(), encoding="utf-8")
    pd.concat([
        coefficient_frame(fit_model, "fit_score"),
        coefficient_frame(rec_model, "recommend"),
    ], ignore_index=True).to_csv(output / "model_coefficients.csv", index=False)

    save_bar_plot(summary, "mean_fit_score", "Mean fit score", output / "fit_score_by_group.png")
    save_bar_plot(summary, "recommendation_rate", "Recommendation rate", output / "recommendation_rate_by_group.png")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze audit results with HC1-robust regressions.")
    parser.add_argument("--input", default="outputs/screening_results.csv")
    parser.add_argument("--output-dir", default="outputs/analysis")
    args = parser.parse_args()
    analyze(args.input, args.output_dir)
    print(f"Analysis written to {args.output_dir}")


if __name__ == "__main__":
    main()
