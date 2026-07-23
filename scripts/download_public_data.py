#!/usr/bin/env python3
"""Download the public source files used to build the audit registries."""

from __future__ import annotations

import argparse
import urllib.request
from pathlib import Path

SOURCES = {
    "census_first_race.xlsx": (
        "https://www2.census.gov/topics/genealogy/2020surnames/"
        "Names2020_FirstNames_RaceHispanic.xlsx"
    ),
    "census_first_sex.xlsx": (
        "https://www2.census.gov/topics/genealogy/2020surnames/"
        "Names2020_FirstNames_Sex.xlsx"
    ),
    "census_last_race.xlsx": (
        "https://www2.census.gov/topics/genealogy/2020surnames/"
        "Names2020_LastNames_RaceHispanic.xlsx"
    ),
    "ssa_names.zip": "https://www.ssa.gov/oact/babynames/names.zip",
    "onet_database_30_3.xlsx.zip": (
        "https://www.onetcenter.org/dl_files/database/db_30_3_excel.zip"
    ),
    "bls_oews_2025_national.xlsx": (
        "https://www.bls.gov/oes/special.requests/oesm25nat.zip"
    ),
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Download Census, SSA, O*NET, and BLS files.")
    parser.add_argument("--output-dir", default="data/raw")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    for filename, url in SOURCES.items():
        target = output / filename
        if target.exists() and not args.overwrite:
            print(f"Keeping existing {target}")
            continue
        print(f"Downloading {url}")
        urllib.request.urlretrieve(url, target)
        print(f"Wrote {target}")


if __name__ == "__main__":
    main()
