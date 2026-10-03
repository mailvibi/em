import argparse
import calendar
import fcntl
import shutil
import sys
import uuid
from pathlib import Path

import pandas as pd

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.categorize_csv import stage3_categorize_csv_data
from src.combine_csv import (
    stage0_1_add_csvfilename,
    stage0_2_normalize_german_columns,
    stage0_3_validate_required_columns,
    stage2_combine_csv_files,
)
from src.constants import (
    AMOUNT_EUR_COLUMN,
    BOOKING_DATE_COLUMN,
    DEFAULT_COLUMNS_TO_KEEP,
    PARTNER_NAME_COLUMN,
    REQUIRED_SOURCE_COLUMNS,
)
from src.csv_to_html import get_expense_report_title, stage6_csv_to_html
from src.filter_csv import (
    stage1_remove_columns_from_csv,
    stage2_remove_columns_from_csv,
    stage4_1_filter_partner_names,
    stage4_filter_and_convert_csv,
)
from src.item_map import get_item_map
from src.summarize_csv import stage5_sum_amounts_by_category


def final_stage(report_path, csv_filename):
    """Rename the stage 6 report using the booking-date year/month periods."""
    report_path = Path(report_path)
    date_df = pd.read_csv(csv_filename)
    booking_dates = pd.to_datetime(
        date_df[BOOKING_DATE_COLUMN], errors="coerce"
    ).dropna()
    periods = sorted(set(zip(booking_dates.dt.year, booking_dates.dt.month)))
    period_names = [
        f"{year}_{calendar.month_name[month]}" for year, month in periods
    ] or ["Unknown_Unknown"]
    final_path = report_path.with_name(f"Expense_{'_'.join(period_names)}.html")
    report_path.replace(final_path)
    return str(final_path)


def _validate_source_directory(statement_directory, output_directory):
    statement_directory = Path(statement_directory).resolve()
    output_directory = Path(output_directory).resolve()

    if output_directory == statement_directory or output_directory.is_relative_to(statement_directory):
        raise ValueError(
            "Output directory must be different from the statement directory and not nested inside it"
        )

    legacy_stage_files = []
    for csv_file in sorted(statement_directory.glob("*.csv")):
        if csv_file.name.startswith(("stage0_", "stage1_", "stage2_", "stage3_", "stage4_", "stage5_", "stage6_")):
            legacy_stage_files.append(csv_file.name)
    if legacy_stage_files:
        raise ValueError(
            "Legacy pipeline CSV artifacts were found in the source directory: "
            + ", ".join(legacy_stage_files)
            + ". Move or rename them before running the pipeline."
        )

    return statement_directory, output_directory


def run_pipeline(
    statement_directory,
    output_directory,
    mapping_file=None,
    progress_callback=None,
    debug=False,
    partner_filter_file=None,
):
    """Run all CSV processing stages in the correct preparation-before-combine order."""
    statement_directory, output_directory = _validate_source_directory(
        statement_directory, output_directory
    )
    output_directory.mkdir(parents=True, exist_ok=True)

    lock_path = output_directory / ".statement_pipeline.lock"
    with lock_path.open("w", encoding="utf-8") as lock_file:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)

            run_directory = output_directory / f".statement_pipeline_run_{uuid.uuid4().hex}"
            prepared_directory = run_directory / "stage0_1"
            stage1_directory = run_directory / "stage1"
            run_directory.mkdir(parents=True, exist_ok=False)
            prepared_directory.mkdir(parents=True, exist_ok=True)
            stage1_directory.mkdir(parents=True, exist_ok=True)

            def report(message):
                if progress_callback is not None:
                    progress_callback(message)

            csv_files = sorted(statement_directory.glob("*.csv"))
            if not csv_files:
                if not debug:
                    shutil.rmtree(run_directory, ignore_errors=True)
                raise ValueError(f"No CSV files found in '{statement_directory}'")

            try:
                report("Preparing statement files...")
                prepared_paths = []
                for csv_file in csv_files:
                    prepared_path = stage0_1_add_csvfilename(csv_file, prepared_directory)
                    prepared_paths.append(prepared_path)
                prepared_paths = stage0_2_normalize_german_columns(prepared_paths)
                for prepared_path in prepared_paths:
                    stage0_3_validate_required_columns(prepared_path, REQUIRED_SOURCE_COLUMNS)

                report("Filtering unused columns...")
                stage1_paths = []
                for prepared_path in prepared_paths:
                    stage1_output = stage1_remove_columns_from_csv(
                        prepared_path, DEFAULT_COLUMNS_TO_KEEP, stage1_directory
                    )
                    stage1_paths.append(stage1_output)

                report("Combining statement files...")
                stage2_output = stage2_combine_csv_files(stage1_paths, run_directory)

                report("Categorizing transactions...")
                item_map = get_item_map(mapping_file)
                stage3_output = stage3_categorize_csv_data(
                    stage2_output, PARTNER_NAME_COLUMN, item_map, run_directory
                )
                report("Filtering outgoing transactions...")
                stage4_output = stage4_filter_and_convert_csv(
                    stage3_output, AMOUNT_EUR_COLUMN, run_directory
                )
                stage5_input = stage4_output
                stage4_1_output = None
                if partner_filter_file is not None:
                    report("Filtering excluded partner names...")
                    stage4_1_output = stage4_1_filter_partner_names(
                        stage4_output, partner_filter_file, run_directory
                    )
                    stage5_input = stage4_1_output
                report("Summarizing categories...")
                stage5_output = stage5_sum_amounts_by_category(stage5_input, run_directory)
                report("Creating HTML report...")
                report_title = get_expense_report_title(stage4_output)
                report_path = stage6_csv_to_html(
                    stage5_output, output_directory, report_title=report_title
                )
                report("Finalizing report filename...")
                report_path = final_stage(report_path, stage4_output)

                if not debug:
                    shutil.rmtree(run_directory, ignore_errors=True)
                return str(report_path)
            except Exception:
                if not debug:
                    shutil.rmtree(run_directory, ignore_errors=True)
                raise
        finally:
            lock_path.unlink(missing_ok=True)
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--statementdir", required=True)
    parser.add_argument("--outputdir", required=True)
    parser.add_argument("--mapping-file")
    parser.add_argument(
        "--partner-filter-file",
        help="Optional JSON file listing Partner Name values to exclude",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Keep intermediate stage CSV files in the output directory",
    )

    args = parser.parse_args()
    report_path = run_pipeline(
        args.statementdir,
        args.outputdir,
        mapping_file=args.mapping_file,
        debug=args.debug,
        partner_filter_file=args.partner_filter_file,
    )
    print(f"Report created: {report_path}")


if __name__ == "__main__":
    main()
