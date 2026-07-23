#!/usr/bin/env python3
"""Build the eight-occupation registry from BLS OEWS and O*NET source files."""

from __future__ import annotations

import argparse
import io
import zipfile
from pathlib import Path

import pandas as pd

SELECTIONS = {
    "51-1011": (
        "production_supervisor",
        "frontline_operational",
        "High school diploma plus related work experience",
        (
            "Manufacturing supervision; operational decision-making; medium wage and "
            "large employment base."
        ),
    ),
    "29-1141": (
        "registered_nurse",
        "frontline_operational",
        "Bachelor's or associate degree plus state licensure",
        (
            "Frontline healthcare; high employment; licensed professional pathway and "
            "high interpersonal intensity."
        ),
    ),
    "49-9071": (
        "maintenance_worker",
        "frontline_operational",
        "High school diploma with technical or on-the-job training",
        (
            "Hands-on facilities work; lower formal education requirement; very large "
            "employment base."
        ),
    ),
    "13-1081": (
        "logistician",
        "frontline_operational",
        "Bachelor's degree",
        (
            "Operational supply-chain role connecting planning, physical flows, vendors, "
            "and field execution."
        ),
    ),
    "13-1111": (
        "management_analyst",
        "knowledge_work",
        "Bachelor's degree",
        "Advisory knowledge work; large employment base; analysis and communication.",
    ),
    "13-1082": (
        "project_management_specialist",
        "knowledge_work",
        "Bachelor's degree",
        (
            "Cross-functional coordination role with broad industry coverage and a large "
            "employment base."
        ),
    ),
    "15-1211": (
        "computer_systems_analyst",
        "knowledge_work",
        "Bachelor's degree",
        (
            "Technical knowledge work combining requirements, systems analysis, and "
            "business processes."
        ),
    ),
    "13-2051": (
        "financial_analyst",
        "knowledge_work",
        "Bachelor's degree",
        "Quantitative finance role with a high wage and analytical screening context.",
    ),
}


def _read_first_excel(zip_path: Path, filename_contains: str) -> pd.DataFrame:
    with zipfile.ZipFile(zip_path) as archive:
        member = next(
            name
            for name in archive.namelist()
            if filename_contains.casefold() in name.casefold()
        )
        return pd.read_excel(io.BytesIO(archive.read(member)))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the BLS and O*NET occupation registry."
    )
    parser.add_argument("--raw-dir", default="data/raw")
    parser.add_argument("--output", default="data/occupations/occupation_registry.csv")
    args = parser.parse_args()

    raw = Path(args.raw_dir)
    bls = _read_first_excel(raw / "bls_oews_2025_national.xlsx", "national")
    onet = _read_first_excel(raw / "onet_database_30_3.xlsx.zip", "occupation data")
    bls.columns = [str(column).strip().upper() for column in bls.columns]
    onet.columns = [str(column).strip() for column in onet.columns]

    onet_code = next(column for column in onet if "Code" in column)
    onet_title = next(column for column in onet if column.casefold() == "title")
    onet["soc_code"] = onet[onet_code].astype(str).str[:7]
    onet_titles = onet.set_index("soc_code")[onet_title].to_dict()

    rows = []
    for soc_code, (occupation_id, group, education, reason) in SELECTIONS.items():
        match = bls.loc[bls["OCC_CODE"].astype(str).eq(soc_code)]
        if match.empty:
            raise ValueError(f"BLS source does not contain {soc_code}")
        record = match.iloc[0]
        title = str(record["OCC_TITLE"])
        rows.append(
            {
                "occupation_id": occupation_id,
                "soc_code": soc_code,
                "occupation_title": title,
                "occupation_group": group,
                "median_wage": int(float(record["A_MEDIAN"])),
                "employment_count": int(float(record["TOT_EMP"])),
                "typical_education": education,
                "onet_version": "30.3",
                "bls_year": 2025,
                "selection_reason": reason,
                "onet_url": (
                    "https://www.onetonline.org/link/summary/" + soc_code + ".00"
                ),
                "onet_title_check": onet_titles.get(soc_code, ""),
            }
        )

    registry = pd.DataFrame(rows)
    group_counts = registry["occupation_group"].value_counts()
    if len(registry) != 8 or group_counts.nunique() != 1:
        raise ValueError("The registry must contain four occupations in each broad group.")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    registry.to_csv(output, index=False)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
