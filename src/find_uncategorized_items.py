#!/usr/bin/env python3
"""Find transaction partners that are not covered by the category mapping."""

import argparse
import sys
from pathlib import Path

import pandas as pd

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.item_map import get_item_map, get_item_map_from_dir


def find_category_for_value(value, mapping_dict):
    """Return the category for a partner value using the same logic as categorize_csv_data."""
    value = str(value)
    return next(
        (category for item, category in mapping_dict.items() if str(item) in value),
        "NO CATEGORY",
    )


def iter_csv_files(csv_path):
    """Yield the CSV files to inspect. Accepts either a single file or a directory."""
    csv_path = Path(csv_path)

    if csv_path.is_file():
        return [csv_path]
    if csv_path.is_dir():
        files = sorted(csv_path.glob("*.csv"))
        if not files:
            raise FileNotFoundError(f"No CSV files found in directory '{csv_path}'")
        return files

    raise FileNotFoundError(f"CSV path '{csv_path}' does not exist")


def extract_uncategorized_items(csv_path, mapping_file=None, output_file=None, mapping_dir=None):
    """Read CSV files, identify partners with no mapping, and return a dataframe of results."""
    mapping_dict = (
        get_item_map_from_dir(mapping_dir)
        if mapping_dir is not None
        else get_item_map(mapping_file)
    )
    frames = []

    for csv_file in iter_csv_files(csv_path):
        try:
            dataframe = pd.read_csv(csv_file)
        except Exception as exc:  # pragma: no cover - defensive error handling
            raise ValueError(f"Could not read '{csv_file}': {exc}") from exc

        if "Partner Name" not in dataframe.columns:
            raise ValueError(f"Column 'Partner Name' not found in '{csv_file}'")
        if "Booking Date" not in dataframe.columns:
            raise ValueError(f"Column 'Booking Date' not found in '{csv_file}'")

        uncategorized = dataframe[
            dataframe["Partner Name"].map(lambda value: find_category_for_value(value, mapping_dict) == "NO CATEGORY")
        ].copy()

        if not uncategorized.empty:
            uncategorized["CSV File Name"] = uncategorized.get(
                "csvfilename", csv_file.name
            )
            frames.append(uncategorized[["Booking Date", "Partner Name", "CSV File Name"]])

    if not frames:
        empty_df = pd.DataFrame(
            columns=["Booking Date", "Partner Name", "CSV File Name", "Occurrences"]
        )
        if output_file is not None:
            empty_df.to_csv(output_file, index=False)
        return empty_df

    combined = pd.concat(frames, ignore_index=True)
    counts = (
        combined.groupby(
            ["Booking Date", "Partner Name", "CSV File Name"],
            dropna=False,
        )
        .size()
        .reset_index(name="Occurrences")
        .sort_values(
            ["Occurrences", "Booking Date", "Partner Name", "CSV File Name"],
            ascending=[False, True, True, True],
        )
        .reset_index(drop=True)
    )

    if output_file is not None:
        counts.to_csv(output_file, index=False)

    return counts


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Scan CSV files and list the partner names that do not match any entry in "
            "shopname_category_mapping.json."
        )
    )
    parser.add_argument("csv_path", help="CSV file or directory containing statement CSV files")
    mapping_source = parser.add_mutually_exclusive_group()
    mapping_source.add_argument(
        "--mapping-file",
        default=None,
        help="Path to the category mapping JSON file. Defaults to shopname_category_mapping.json",
    )
    mapping_source.add_argument(
        "--mapping-dir",
        help="Directory containing category mapping JSON files",
    )
    parser.add_argument(
        "--output",
        help="Optional CSV path to write the uncategorized partner names and their occurrence count",
    )
    args = parser.parse_args()

    result = extract_uncategorized_items(
        args.csv_path,
        mapping_file=args.mapping_file,
        output_file=args.output,
        mapping_dir=args.mapping_dir,
    )

    if result.empty:
        print("No uncategorized items found.")
        return

    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
