import argparse
from pathlib import Path

from categorize_csv import stage3_categorize_csv_data
from combine_csv import stage1_combine_csv_files
from csv_to_html import stage6_csv_to_html
from filter_csv import stage2_remove_columns_from_csv, stage4_filter_and_convert_csv
from item_map import get_item_map
from summarize_csv import stage5_sum_amounts_by_category


DEFAULT_COLUMNS_TO_KEEP = [
    "Booking Date",
    "Partner Name",
    "Amount (EUR)",
    "csvfilename",
]


def run_pipeline(statement_directory, output_directory, mapping_file=None, progress_callback=None):
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
    report("Summarizing categories...")
    stage5_output = stage5_sum_amounts_by_category(stage4_output, output_directory)
    report("Creating HTML report...")
    return stage6_csv_to_html(stage5_output, output_directory)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--statementdir", required=True)
    parser.add_argument("--outputdir", required=True)
    parser.add_argument("--mapping-file")
    args = parser.parse_args()
    report_path = run_pipeline(
        args.statementdir, args.outputdir, mapping_file=args.mapping_file
    )
    print(f"Report created: {report_path}")


if __name__ == "__main__":
    main()
