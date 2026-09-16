import argparse

from categorize_csv import categorize_csv_data
from combine_csv import combine_csv_files
from csv_to_html import csv_to_html
from filter_csv import filter_and_convert_csv, remove_columns_from_csv
from item_map import get_item_map
from summarize_csv import sum_amounts_by_category


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--statementdir", required=True)
    parser.add_argument("--outputdir", required=True)
    args = parser.parse_args()

    columns_to_remove = [
        "Value Date",
        "Partner Iban",
        "Type",
        "Payment Reference",
        "Account Name",
        "Original Amount",
        "Original Currency",
        "Exchange Rate",
    ]

    stage1_output = combine_csv_files(args.statementdir, args.outputdir)
    stage2_output = remove_columns_from_csv(stage1_output, columns_to_remove, args.outputdir)
    item_map = get_item_map()
    stage3_output = categorize_csv_data(stage2_output, "Partner Name", item_map, args.outputdir)
    stage4_output = filter_and_convert_csv(stage3_output, "Amount (EUR)", args.outputdir)
    stage5_output = sum_amounts_by_category(stage4_output, args.outputdir)
    csv_to_html(stage5_output)


if __name__ == "__main__":
    main()
