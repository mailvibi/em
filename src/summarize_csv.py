import os
from pathlib import Path

import pandas as pd

from src.constants import (
    AMOUNT_EUR_COLUMN,
    CATEGORY_COLUMN,
    REQUIRED_SUMMARY_COLUMNS,
    TOTAL_AMOUNT_EUR_COLUMN,
)


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

        required_columns = REQUIRED_SUMMARY_COLUMNS
        missing_columns = [column for column in required_columns if column not in df.columns]
        if missing_columns:
            raise Exception(f"Required columns not found: {missing_columns}")

        df[AMOUNT_EUR_COLUMN] = pd.to_numeric(df[AMOUNT_EUR_COLUMN], errors="coerce")
        original_rows = len(df)
        df = df.dropna(subset=[AMOUNT_EUR_COLUMN])
        if len(df) < original_rows:
            print(
                f"Warning: Removed {original_rows - len(df)} rows with non-numeric "
                f"'{AMOUNT_EUR_COLUMN}' values"
            )

        summary_df = (
            df.groupby(CATEGORY_COLUMN)[AMOUNT_EUR_COLUMN]
            .sum()
            .reset_index(name=TOTAL_AMOUNT_EUR_COLUMN)
            .sort_values(TOTAL_AMOUNT_EUR_COLUMN, ascending=False)
        )

        input_file = Path(csv_filename)
        output_path = Path(output_directory) / "stage5_sum_amounts_by_category_output.csv"
        summary_df.to_csv(output_path, index=False)

        print(f"Category summary saved to: {output_path}")
        print(f"Total categories: {len(summary_df)}")
        print(f"Grand total: {summary_df[TOTAL_AMOUNT_EUR_COLUMN].sum():.2f} EUR")
        return output_path
    except Exception as error:
        raise Exception(f"Error processing CSV file: {error}") from error