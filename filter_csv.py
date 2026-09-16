import os
from pathlib import Path

import pandas as pd


def remove_columns_from_csv(csv_file_path, columns_to_remove, output_directory):
    """Remove selected columns and save the modified CSV."""
    os.makedirs(output_directory, exist_ok=True)
    df = pd.read_csv(csv_file_path)
    input_file = Path(csv_file_path)
    columns_to_drop = [column for column in columns_to_remove if column in df.columns]

    if columns_to_drop:
        df_modified = df.drop(columns=columns_to_drop)
        print(f"Removed columns: {columns_to_drop}")
    else:
        df_modified = df.copy()
        print("No matching columns found to remove")

    output_path = Path(output_directory) / f"stage2_{input_file.stem}_modified.csv"
    df_modified.to_csv(output_path, index=False)

    print(f"Modified CSV saved to: {output_path}")
    print(f"Original columns: {len(df.columns)}, Remaining columns: {len(df_modified.columns)}")
    return output_path


def filter_and_convert_csv(csv_filename, column_name, output_directory):
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
        output_path = Path(output_directory) / f"{input_file.stem}_filtered.csv"
        df_filtered.to_csv(output_path, index=False)

        print(f"Processed CSV saved to: {output_path}")
        print(f"Original rows: {len(df)}, Remaining rows: {len(df_filtered)}")
        return output_path
    except Exception as error:
        raise Exception(f"Error processing CSV file: {error}") from error