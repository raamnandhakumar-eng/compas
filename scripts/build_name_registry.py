#!/usr/bin/env python3
"""Rebuild the perceived-name source registry from downloaded public files."""

from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path

import pandas as pd

CANDIDATES = {
    "signal_a": [("Arjun", "Patel", "South Asian"), ("Rohan", "Shah", "South Asian")],
    "signal_b": [("Ethan", "Miller", "White"), ("Lucas", "Bennett", "White")],
    "signal_c": [("Jamal", "Reed", "Black"), ("Darius", "Cole", "Black")],
    "signal_d": [
        ("Carlos", "Garcia", "Hispanic or Latino"),
        ("Mateo", "Rodriguez", "Hispanic or Latino"),
    ],
}


def _normal(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value).casefold()).strip("_")


def _read_census(path: Path) -> pd.DataFrame:
    frame = pd.read_excel(path)
    frame.columns = [_normal(column) for column in frame.columns]
    name_column = next(column for column in frame if column in {"name", "firstname", "lastname"})
    frame[name_column] = frame[name_column].astype(str).str.strip().str.casefold()
    return frame.rename(columns={name_column: "name_key"})


def _find_column(frame: pd.DataFrame, required_tokens: tuple[str, ...]) -> str:
    matches = [
        column
        for column in frame.columns
        if all(token in column for token in required_tokens)
    ]
    if not matches:
        raise ValueError(f"Could not find Census column containing {required_tokens}")
    return matches[0]


def _count_column(frame: pd.DataFrame) -> str:
    for candidate in ("count", "number", "frequency"):
        if candidate in frame.columns:
            return candidate
    return _find_column(frame, ("count",))


def _dominant_group(row: pd.Series, frame: pd.DataFrame) -> tuple[str, float]:
    group_tokens = {
        "White": ("white",),
        "Black": ("black",),
        "Asian or Pacific Islander": ("asian",),
        "American Indian or Alaska Native": ("american_indian",),
        "Hispanic or Latino": ("hispanic",),
        "Two or more races": ("two", "race"),
    }
    values = {}
    for label, tokens in group_tokens.items():
        try:
            column = _find_column(frame, tokens)
        except ValueError:
            continue
        values[label] = float(pd.to_numeric(row[column], errors="coerce"))
    if not values:
        raise ValueError("No Census race or Hispanic-origin percentage columns were found.")
    label = max(values, key=values.get)
    share = values[label]
    if share > 1:
        share /= 100
    return label, share


def _ssa_counts(path: Path) -> dict[str, int]:
    totals: dict[str, int] = {}
    with zipfile.ZipFile(path) as archive:
        for member in archive.namelist():
            if not re.fullmatch(r"yob\d{4}\.txt", Path(member).name):
                continue
            with archive.open(member) as handle:
                frame = pd.read_csv(handle, names=["name", "sex", "count"])
            male = frame[frame["sex"].eq("M")]
            for row in male.itertuples(index=False):
                key = str(row.name).casefold()
                totals[key] = totals.get(key, 0) + int(row.count)
    return totals


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Census and SSA name registry.")
    parser.add_argument("--raw-dir", default="data/raw")
    parser.add_argument("--output", default="data/name_validation/name_candidates.csv")
    args = parser.parse_args()

    raw = Path(args.raw_dir)
    first_race = _read_census(raw / "census_first_race.xlsx")
    first_sex = _read_census(raw / "census_first_sex.xlsx")
    last_race = _read_census(raw / "census_last_race.xlsx")
    ssa = _ssa_counts(raw / "ssa_names.zip")

    first_count = _count_column(first_race)
    first_sex_count = _count_column(first_sex)
    last_count = _count_column(last_race)
    male_column = _find_column(first_sex, ("male",))

    rows = []
    for signal_group, names in CANDIDATES.items():
        for first_name, last_name, perceived_signal in names:
            first_key = first_name.casefold()
            last_key = last_name.casefold()
            first_row = first_race.loc[first_race["name_key"].eq(first_key)].iloc[0]
            sex_row = first_sex.loc[first_sex["name_key"].eq(first_key)].iloc[0]
            last_row = last_race.loc[last_race["name_key"].eq(last_key)].iloc[0]
            first_group, first_share = _dominant_group(first_row, first_race)
            last_group, last_share = _dominant_group(last_row, last_race)
            male_share = float(pd.to_numeric(sex_row[male_column], errors="coerce"))
            if male_share > 1:
                male_share /= 100
            full_name = f"{first_name} {last_name}"
            rows.append(
                {
                    "candidate_id": f"{first_key}_{last_key}",
                    "signal_group": signal_group,
                    "perceived_name_signal": perceived_signal,
                    "first_name": first_name,
                    "last_name": last_name,
                    "full_name": full_name,
                    "census_first_count": int(first_row[first_count]),
                    "census_first_group": first_group,
                    "census_first_group_share": first_share,
                    "census_first_sex": "Male",
                    "census_first_sex_share": male_share,
                    "census_last_count": int(last_row[last_count]),
                    "census_last_group": last_group,
                    "census_last_group_share": last_share,
                    "ssa_frequency": int(ssa.get(first_key, 0)),
                    "source_year": "2020;1880-latest",
                    "source_file": (
                        "Names2020_FirstNames_RaceHispanic.xlsx;"
                        "Names2020_FirstNames_Sex.xlsx;"
                        "Names2020_LastNames_RaceHispanic.xlsx;SSA names.zip"
                    ),
                    "screening_status": "source_screened_pending_pretest",
                    "notes": (
                        "Aggregate source screen only; not an actual demographic identity. "
                        "Perception pretest required."
                    ),
                }
            )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    registry = pd.DataFrame(rows)
    if (registry[["census_first_count", "census_last_count", "ssa_frequency"]] < 100).any().any():
        raise ValueError("A candidate name is too rare for the locked source-screen rule.")
    registry.to_csv(output, index=False)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
