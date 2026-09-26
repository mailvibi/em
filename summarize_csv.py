import os
from pathlib import Path

import pandas as pd


def stage5_sum_amounts_by_category(csv_filename, output_directory):
    """Sum amounts by category and save the summary CSV."""
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

        required_columns = ["Amount (EUR)", "CATAGORY"]
        missing_columns = [column for column in required_columns if column not in df.columns]
        if missing_columns:
            raise Exception(f"Required columns not found: {missing_columns}")

        df["Amount (EUR)"] = pd.to_numeric(df["Amount (EUR)"], errors="coerce")
        original_rows = len(df)
        df = df.dropna(subset=["Amount (EUR)"])
        if len(df) < original_rows:
            print(f"Warning: Removed {original_rows - len(df)} rows with non-numeric 'Amount (EUR)' values")

        summary_df = (
            df.groupby("CATAGORY")["Amount (EUR)"]
            .sum()
            .reset_index(name="Total Amount (EUR)")
            .sort_values("Total Amount (EUR)", ascending=False)
        )

        input_file = Path(csv_filename)
        output_path = Path(output_directory) / "stage5_sum_amounts_by_category_output.csv"
        summary_df.to_csv(output_path, index=False)

        print(f"Category summary saved to: {output_path}")
        print(f"Total categories: {len(summary_df)}")
        print(f"Grand total: {summary_df['Total Amount (EUR)'].sum():.2f} EUR")
        return output_path
    except Exception as error:
        raise Exception(f"Error processing CSV file: {error}") from error