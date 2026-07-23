from __future__ import annotations

import argparse
import hashlib
import itertools
from pathlib import Path

import pandas as pd

from .common import load_config, stable_id


def _qualification_hash(row: pd.Series) -> str:
    fields = [
        "occupation_id",
        "target_role",
        "years_experience",
        "education",
        "skills",
        "employer_history",
        "experience_summary",
        "achievement",
    ]
    payload = "\n".join(str(row.get(field, "")) for field in fields)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _treatment_text(education_pathway: str, gap_months: int, education: str) -> tuple[str, str]:
    pathway_text = (
        f"Traditional pathway; completed {education} through full-time study"
        if education_pathway == "traditional"
        else f"Non-traditional pathway; completed {education} through part-time study"
    )
    gap_text = (
        "Continuous work history; no career break was recorded"
        if gap_months == 0
        else "Twelve-month career break; return to work was completed"
    )
    return pathway_text, gap_text


def build_resume_text(
    row: pd.Series,
    name: str,
    education_pathway: str,
    gap_months: int,
) -> str:
    pathway_text, gap_text = _treatment_text(
        education_pathway,
        gap_months,
        str(row["education"]),
    )
    return "\n".join(
        [
            f"Candidate: {name}",
            f"Target role: {row['target_role']}",
            f"Experience: {row['years_experience']} years",
            f"Education: {pathway_text}",
            f"Employment continuity: {gap_text}",
            f"Skills: {row['skills']}",
            f"Employer history: {row['employer_history']}",
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
        profile_slot = int(row["profile_slot"])
        for signal_group, candidate_names in names.items():
            if len(candidate_names) < 2:
                raise ValueError(f"{signal_group} must contain at least two candidate names.")
            name = candidate_names[(profile_slot - 1) % len(candidate_names)]
            for pathway, gap in itertools.product(pathways, gaps):
                matched_set_id = str(row["matched_set_id"])
                resume_id = stable_id(matched_set_id, signal_group, pathway, gap)
                resume_text = build_resume_text(row, name, pathway, int(gap))
                records.append(
                    {
                        "resume_id": resume_id,
                        "matched_set_id": matched_set_id,
                        "base_profile_id": row["base_profile_id"],
                        "profile_slot": profile_slot,
                        "template_id": row["template_id"],
                        "occupation_id": row["occupation_id"],
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
                        "qualification_hash": _qualification_hash(row),
                        "resume_word_count": len(resume_text.split()),
                        "resume_text": resume_text,
                    }
                )

    result = pd.DataFrame.from_records(records)
    if result.empty:
        raise ValueError("No resume permutations were generated.")

    expected_per_set = len(names) * len(pathways) * len(gaps)
    set_sizes = result.groupby("matched_set_id").size()
    if not set_sizes.eq(expected_per_set).all():
        raise ValueError("Treatment allocation is incomplete within one or more matched sets.")
    if result.groupby("matched_set_id")["qualification_hash"].nunique().max() != 1:
        raise ValueError("Qualifications changed within a matched set.")

    return result.sort_values(
        [
            "occupation_id",
            "matched_set_id",
            "signal_group",
            "education_pathway",
            "career_gap_months",
        ]
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
    print(
        f"Wrote {len(resumes)} matched resumes across "
        f"{resumes['occupation_id'].nunique()} occupations to {output}"
    )


if __name__ == "__main__":
    main()
