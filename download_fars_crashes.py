"""Download FARS (NHTSA fatal crash) data for a range of years, one JSON file per year.

Tries the NHTSA CrashAPI first (GetFARSData, dataset=Accident) and falls back to
the static FARS bulk CSV zip if the API is unreachable or blocked.
Settings (years, state, output folder) are hardcoded in main().
"""

import io
import json
import zipfile
from pathlib import Path

import pandas as pd
import requests

CRASH_API = "https://crashviewer.nhtsa.dot.gov/CrashAPI/FARSData/GetFARSData"
BULK_URL = "https://static.nhtsa.gov/nhtsa/downloads/FARS/{year}/National/FARS{year}NationalCSV.zip"
HEADERS = {"User-Agent": "Mozilla/5.0 (DrivingBuddy FARS downloader)"}


def fetch_api(year: int, state_fips: int) -> list[dict]:
    params = {
        "dataset": "Accident",
        "FromYear": year,
        "ToYear": year,
        "State": state_fips,
        "format": "json",
    }
    response = requests.get(CRASH_API, params=params, headers=HEADERS, timeout=120)
    response.raise_for_status()
    # The API wraps records as {"Results": [[{...}, ...]]}
    return response.json()["Results"][0]


def fetch_bulk(year: int, state_fips: int) -> list[dict]:
    response = requests.get(BULK_URL.format(year=year), headers=HEADERS, timeout=300)
    response.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        name = next(n for n in archive.namelist() if n.lower().endswith("accident.csv"))
        with archive.open(name) as f:
            # utf-8-sig strips the BOM that would otherwise corrupt the STATE column name
            df = pd.read_csv(f, encoding="utf-8-sig", encoding_errors="replace", low_memory=False)
    df = df[df["STATE"] == state_fips]
    # Round-trip through to_json so numpy types and NaN become JSON-safe (NaN -> null)
    return json.loads(df.to_json(orient="records"))


def download(year: int, state_fips: int) -> list[dict]:
    try:
        records = fetch_api(year, state_fips)
        print(f"{year}: {len(records)} crashes (CrashAPI)")
    except (requests.RequestException, KeyError, IndexError, ValueError) as exc:
        print(f"CrashAPI unavailable ({type(exc).__name__}); using bulk file instead")
        records = fetch_bulk(year, state_fips)
        print(f"{year}: {len(records)} crashes (bulk file)")
    return records


def main() -> None:
    first_year = 2014
    last_year = 2024
    state_fips = 19  # Iowa
    output_dir = Path(__file__).parent / "Iowa_crashes"

    output_dir.mkdir(parents=True, exist_ok=True)
    for year in range(first_year, last_year + 1):
        records = download(year, state_fips)
        output = output_dir / f"iowa_fars_{year}.json"
        with open(output, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)
        print(f"Saved {len(records)} crashes to {output}")


if __name__ == "__main__":
    main()
