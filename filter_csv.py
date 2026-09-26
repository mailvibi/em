import os
from pathlib import Path

import pandas as pd


def stage2_remove_columns_from_csv(csv_file_path, columns_to_keep, output_directory):
    """Remove selected columns and save the modified CSV."""
    os.makedirs(output_directory, exist_ok=True)
    df = pd.read_csv(csv_file_path)
    input_file = Path(csv_file_path)
    existing_columns_to_keep = [column for column in columns_to_keep if column in df.columns]
    df_modified = df.loc[:, existing_columns_to_keep]
    columns_removed = [column for column in df.columns if column not in existing_columns_to_keep]
    print(f"Removed columns: {columns_removed}")

    output_path = Path(output_directory) / "stage2_remove_columns_from_csv_output.csv"
    df_modified.to_csv(output_path, index=False)

    print(f"Modified CSV saved to: {output_path}")
    print(f"Original columns: {len(df.columns)}, Remaining columns: {len(df_modified.columns)}")
    return output_path


def stage4_filter_and_convert_csv(csv_filename, column_name, output_directory):
    """Keep negative values, convert them to positive, and save the CSV."""
    try:
        os.makedirs(output_directory, exist_ok=True)
        try:
            df = pd.read_csv(csv_filename)
        except FileNotFoundError as error:
            raise Exception(f"CSV file '{csv_filename}' not found") from error
        except pd.errors.EmptyDataError as error:
            raise Exception(f"CSV file '{csv_filename}' is empty") from error
        except Exception as error:
            raise Exception(f"Error reading CSV file '{csv_filename}': {error}") from error

        if column_name not in df.columns:
            raise Exception(f"Column '{column_name}' not found in CSV file")

        df[column_name] = pd.to_numeric(df[column_name], errors="coerce")
        if df[column_name].isna().any():
            raise Exception(f"Column '{column_name}' contains non-numeric values that cannot be processed")

        df_filtered = df[df[column_name] < 0].copy()
        df_filtered[column_name] = df_filtered[column_name].abs()

        if df_filtered.empty:
            print(f"Warning: No negative values found in column '{column_name}'. Output file will be empty.")

        input_file = Path(csv_filename)
        output_path = Path(output_directory) / "stage4_filter_and_convert_csv_output.csv"
        df_filtered.to_csv(output_path, index=False)

        print(f"Processed CSV saved to: {output_path}")
        print(f"Original rows: {len(df)}, Remaining rows: {len(df_filtered)}")
        return output_path
    except Exception as error:
        raise Exception(f"Error processing CSV file: {error}") from error