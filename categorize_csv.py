import os
from pathlib import Path

import pandas as pd


def stage3_categorize_csv_data(csv_filename, column_name, mapping_dict, output_directory):
    """Add categories based on matching mapping keys and save the CSV."""
    os.makedirs(output_directory, exist_ok=True)
    df = pd.read_csv(csv_filename)

    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in CSV file")

    def find_category(value):
        value = str(value)
        return next(
            (category for item, category in mapping_dict.items() if str(item) in value),
            "NO CATEGORY",
        )

    df["CATEGORY"] = df[column_name].map(find_category)

    input_file = Path(csv_filename)
    output_path = Path(output_directory) / "stage3_categorize_csv_data_output.csv"
    df.to_csv(output_path, index=False)

    print(f"Categorized CSV saved to: {output_path}")
    print(f"Total rows processed: {len(df)}")
    return str(output_path)