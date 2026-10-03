import argparse
from pathlib import Path

from categorize_csv import stage3_categorize_csv_data
from combine_csv import stage1_combine_csv_files
from csv_to_html import get_expense_report_title, stage6_csv_to_html
from filter_csv import (
    stage2_remove_columns_from_csv,
    stage4_1_filter_partner_names,
    stage4_filter_and_convert_csv,
)
from item_map import get_item_map
from summarize_csv import stage5_sum_amounts_by_category


DEFAULT_COLUMNS_TO_KEEP = [
    "Booking Date",
    "Partner Name",
    "Amount (EUR)",
    "csvfilename",
]



def run_pipeline(
    statement_directory,
    output_directory,
    mapping_file=None,
    progress_callback=None,
    debug=False,
    partner_filter_file=None,
):
    """Run all CSV processing stages and return the generated HTML path."""
    statement_directory = Path(statement_directory)
    output_directory = Path(output_directory)

    def report(message):
        if progress_callback is not None:
            progress_callback(message)

    report("Combining statement files...")
    stage1_output = stage1_combine_csv_files(statement_directory, output_directory)
    if stage1_output is None:
        raise ValueError(f"No CSV files found in '{statement_directory}'")

    report("Removing unused columns...")
    stage2_output = stage2_remove_columns_from_csv(
        stage1_output, DEFAULT_COLUMNS_TO_KEEP, output_directory
    )
    report("Categorizing transactions...")
    item_map = get_item_map(mapping_file)
    stage3_output = stage3_categorize_csv_data(
        stage2_output, "Partner Name", item_map, output_directory
    )
    report("Filtering outgoing transactions...")
    stage4_output = stage4_filter_and_convert_csv(
        stage3_output, "Amount (EUR)", output_directory
    )
    stage5_input = stage4_output
    stage4_1_output = None
    if partner_filter_file is not None:
        report("Filtering excluded partner names...")
        stage4_1_output = stage4_1_filter_partner_names(
            stage4_output, partner_filter_file, output_directory
        )
        stage5_input = stage4_1_output
    report("Summarizing categories...")
    stage5_output = stage5_sum_amounts_by_category(stage5_input, output_directory)
    report("Creating HTML report...")
    report_title = get_expense_report_title(stage4_output)
    report_path = stage6_csv_to_html(
        stage5_output, output_directory, report_title=report_title
    )

    if not debug:
        stage_outputs = [stage1_output, stage2_output, stage3_output, stage4_output]
        if stage4_1_output is not None:
            stage_outputs.append(stage4_1_output)
        for stage_output in stage_outputs:
            Path(stage_output).unlink(missing_ok=True)

    return report_path
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
