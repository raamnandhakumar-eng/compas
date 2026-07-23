from __future__ import annotations

import argparse
import itertools
from pathlib import Path

import pandas as pd

from .common import load_config, stable_id


def build_resume_text(row: pd.Series, name: str, education_pathway: str, gap_months: int) -> str:
    pathway_text = (
        row["education"]
        if education_pathway == "traditional"
        else f"Non-traditional pathway; completed {row['education']} through part-time study"
    )
    gap_text = "No employment gap" if gap_months == 0 else f"Career break: {gap_months} months"
    return "\n".join(
        [
            f"Candidate: {name}",
            f"Target role: {row['target_role']}",
            f"Experience: {row['years_experience']} years",
            f"Education: {pathway_text}",
            f"Employment continuity: {gap_text}",
            f"Skills: {row['skills']}",
            f"Experience summary: {row['experience_summary']}",
            f"Selected achievement: {row['achievement']}",
        ]
    )


def generate_permutations(config_path: str, templates_path: str) -> pd.DataFrame:
    config = load_config(config_path)
    templates = pd.read_csv(templates_path)
    names = config["signals"]["names"]
    pathways = config["signals"]["education_pathway"]
    gaps = config["signals"]["career_gap_months"]

    records: list[dict[str, object]] = []
    for _, row in templates.iterrows():
        for signal_group, candidate_names in names.items():
            for name, pathway, gap in itertools.product(candidate_names, pathways, gaps):
                resume_id = stable_id(row["template_id"], signal_group, name, pathway, gap)
                records.append(
                    {
                        "resume_id": resume_id,
                        "template_id": row["template_id"],
                        "occupation_tier": row["occupation_tier"],
                        "target_role": row["target_role"],
                        "onet_soc_code": row.get("onet_soc_code", ""),
                        "onet_title": row.get("onet_title", ""),
                        "source_url": row.get("source_url", ""),
                        "signal_group": signal_group,
                        "candidate_name": name,
                        "education_pathway": pathway,
                        "career_gap_months": int(gap),
                        "years_experience": int(row["years_experience"]),
                        "resume_text": build_resume_text(row, name, pathway, int(gap)),
                    }
                )

    result = pd.DataFrame.from_records(records)
    if result.empty:
        raise ValueError("No resume permutations were generated.")
    return result.sort_values(
        ["template_id", "signal_group", "candidate_name", "education_pathway", "career_gap_months"]
    ).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate matched synthetic resume permutations.")
    parser.add_argument("--config", default="config/audit.yaml")
    parser.add_argument("--templates", default="data/templates/resume_templates.csv")
    args = parser.parse_args()

    config = load_config(args.config)
    output = Path(config.get("output_resumes", "outputs/resume_permutations.csv"))
    output.parent.mkdir(parents=True, exist_ok=True)
    resumes = generate_permutations(args.config, args.templates)
    resumes.to_csv(output, index=False)
    print(f"Wrote {len(resumes)} matched resumes to {output}")


if __name__ == "__main__":
    main()
