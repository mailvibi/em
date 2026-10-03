import os
from pathlib import Path

import pandas as pd


def stage0_1_add_csvfilename(csv_file_path, output_directory):
    """Add the source filename stem as csvfilename and save a prepared copy."""
    input_path = Path(csv_file_path)
    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)
    df["csvfilename"] = input_path.stem
    output_path = output_dir / f"{input_path.stem}_stage0_1_prepared.csv"
    df.to_csv(output_path, index=False)
    return output_path


def stage0_2_passthrough(file_paths):
    """Explicit no-op pass-through for the preparation pipeline stage."""
    return list(file_paths)


def stage0_3_validate_required_columns(csv_file_path, required_columns=None):
    """Validate that a prepared CSV contains the required source columns."""
    if required_columns is None:
        required_columns = ["Booking Date", "Partner Name", "Amount (EUR)"]

    input_path = Path(csv_file_path)
    df = pd.read_csv(input_path)
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(
            f"CSV file '{input_path.name}' missing required columns: {missing_columns}"
        )
    return True


def stage1_combine_csv_files(csvdir, opdir):
    """Backward-compatible wrapper for the legacy single-step combine behavior."""
    os.makedirs(opdir, exist_ok=True)
    csv_files = sorted(Path(csvdir).glob("*.csv"))

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


def stage2_combine_csv_files(csv_files, output_directory):
    """Combine a list of already-prepared CSV files into one output CSV."""
    csv_files = [Path(csv_file) for csv_file in csv_files]
    if not csv_files:
        raise ValueError("No CSV files available to combine")

    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    all_dataframes = [pd.read_csv(csv_file) for csv_file in csv_files]
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    output_path = output_dir / "stage2_combine_csv_files_output.csv"
    combined_df.to_csv(output_path, index=False)
    return output_path