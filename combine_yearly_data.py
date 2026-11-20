"""Combine yearly JSON files (e.g. iowa_fars_2022.json) into one JSON file.

Usage:
    python combine_yearly_data.py [FOLDER] [-o OUTPUT_NAME] <- will be in folder

If FOLDER or OUTPUT_NAME are omitted, they are asked for interactively.
Each yearly file must contain a JSON list; the lists are concatenated in
year order and written to OUTPUT_NAME inside FOLDER.
"""
import argparse
import json
import re
import sys
from pathlib import Path

YEAR_RE = re.compile(r"(?<!\d)((?:19|20)\d{2})(?!\d)")


def find_yearly_files(folder, output_path):
    """Return [(year, path)] for .json files with exactly one year in the name."""
    found = []
    for path in folder.glob("*.json"):
        if path.resolve() == output_path.resolve():
            continue
        years = YEAR_RE.findall(path.stem)
        if len(years) == 1:
            found.append((int(years[0]), path))
        elif len(years) > 1:
            print(f"Skipping {path.name}: multiple years in name (already combined?)")
    return sorted(found)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("folder", nargs="?", help="folder containing yearly JSON files")
    parser.add_argument("-o", "--output", help="name of the combined JSON file")
    args = parser.parse_args()

    folder = Path(args.folder or input("Folder with yearly JSON files: ").strip().strip('"'))
    if not folder.is_dir():
        sys.exit(f"Error: '{folder}' is not a folder.")

    output_name = args.output or input("Name of the combined JSON file: ").strip().strip('"')
    if not output_name:
        sys.exit("Error: no output file name given.")
    if not output_name.lower().endswith(".json"):
        output_name += ".json"
    output_path = folder / Path(output_name).name

    files = find_yearly_files(folder, output_path)
    if not files:
        sys.exit(f"Error: no .json files with a year in the name found in '{folder}'.")

    combined = []
    for year, path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            sys.exit(f"Error: {path.name} is not valid JSON: {e}")
        if not isinstance(data, list):
            sys.exit(f"Error: {path.name} does not contain a JSON list.")
        print(f"{path.name}: {len(data)} records")
        combined.extend(data)

    output_path.write_text(json.dumps(combined, indent=2), encoding="utf-8")
    print(f"Wrote {len(combined)} records from {len(files)} files to {output_path}")


if __name__ == "__main__":
    main()
