# Statement Studio

Statement Studio converts bank statement CSV exports into a categorized, summarized HTML report.

It combines multiple statement files, removes noisy columns, matches transaction payees to categories, filters outgoing items, and produces a report grouped by category with totals.

## Features

- Combine multiple statement CSV files into one dataset
- Remove irrelevant columns before processing
- Match merchant names against a category mapping JSON
- Filter transaction amounts and summarize by category
- Generate an HTML report ready for review
- Provide both a CLI interface and a desktop GUI

## Project layout

- `sm.py` — command-line pipeline entry point
- `gui.py` — Tkinter desktop application
- `combine_csv.py` — merge statement CSV files
- `filter_csv.py` — remove columns and filter converted values
- `categorize_csv.py` — assign category labels based on merchant text
- `summarize_csv.py` — aggregate totals by category
- `csv_to_html.py` — create the final HTML report
- `shopname_category_mapping.json` — default merchant-to-category rules
- `build_executables.sh` — rebuild GUI and CLI executables with PyInstaller

## Requirements

Install the project dependencies with:

```bash
python -m pip install -r requirements.txt
```

## Command-line usage

```bash
python sm.py --statementdir ./statements --outputdir ./output --mapping-file ./shopname_category_mapping.json
```

This generates an HTML report in the output folder.

## GUI usage

```bash
python gui.py
```

The GUI lets you choose the statement folder, output folder, and mapping file, then starts the processing pipeline from a desktop window.

## Building executables

A bundled build script is included for Linux:

```bash
./build_executables.sh
```

The script creates:

- `dist/statement-studio` — GUI executable
- `dist/statement-pipeline` — CLI executable

## Notes

The project expects a Python 3.12 environment and uses the bundled `shopname_category_mapping.json` file as the default mapping source.
