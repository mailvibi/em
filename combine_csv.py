import os
from pathlib import Path

import pandas as pd


def stage1_combine_csv_files(csvdir, opdir):
    """Combine CSV files from ``csvdir`` and save the result to ``opdir``."""
    os.makedirs(opdir, exist_ok=True)
    csv_files = list(Path(csvdir).glob("*.csv"))

    if not csv_files:
        print(f"No CSV files found in {csvdir}")
        return

    all_dataframes = []
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            df["csvfilename"] = csv_file.stem
            all_dataframes.append(df)
            print(f"Processed: {csv_file.name}")
        except Exception as error:
            raise Exception(f"Error processing {csv_file.name}: {error}") from error

    combined_df = pd.concat(all_dataframes, ignore_index=True)
    output_file = Path(opdir) / "stage1_combine_csv_files_output.csv"
    combined_df.to_csv(output_file, index=False)

    print(f"Combined CSV file saved to: {output_file}")
    print(f"Total rows: {len(combined_df)}")
    print(f"Total columns: {len(combined_df.columns)}")
    return output_file