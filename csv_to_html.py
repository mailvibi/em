import calendar
import os
from pathlib import Path

import pandas as pd


def get_expense_report_title(csv_filename):
    """Build an expense report title from transaction booking dates."""
    try:
        date_df = pd.read_csv(csv_filename)
        if "Booking Date" not in date_df.columns:
            raise Exception(f"Column 'Booking Date' not found in '{csv_filename}'")

        booking_dates = pd.to_datetime(date_df["Booking Date"], errors="coerce").dropna()
        years = sorted(booking_dates.dt.year.unique())
        months = sorted(booking_dates.dt.month.unique())
        year_text = ", ".join(str(year) for year in years) or "Unknown"
        month_text = ", ".join(calendar.month_name[month] for month in months) or "Unknown"
        return f"Expense Report : Year - {year_text} , Month[s] : {month_text}"
    except Exception as error:
        raise Exception(f"Error extracting report dates from '{csv_filename}': {error}") from error


def stage6_csv_to_html(csv_filename, output_directory=None, report_title="CSV Data"):
    """
    Convert a CSV file to an HTML file with table formatting.

    Args:
        csv_filename (str): Path to the input CSV file
        output_directory (str, optional): Directory where the HTML file will be saved.
                                        If None, saves in the same directory as input CSV.

    Returns:
        str: Filename of the newly created HTML file

    Raises:
        Exception: For file not found or other processing errors
    """
    try:
        # Read the CSV file
        try:
            df = pd.read_csv(csv_filename)
        except FileNotFoundError:
            raise Exception(f"CSV file '{csv_filename}' not found")
        except pd.errors.EmptyDataError:
            raise Exception(f"CSV file '{csv_filename}' is empty")
        except Exception as e:
            raise Exception(f"Error reading CSV file '{csv_filename}': {e}")

        input_path = Path(csv_filename)

        # Determine output directory
        if output_directory is None:
            output_dir = input_path.parent
        else:
            output_dir = Path(output_directory)
            os.makedirs(output_dir, exist_ok=True)

        # Create output filename
        output_filename = "stage6_csv_to_html_output.html"
        output_path = output_dir / output_filename

        # Create HTML content with styling
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
            color: #495057;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        tr:hover {{
            background-color: #e9ecef;
        }}
        .info {{
            margin-top: 20px;
            padding: 10px;
            background-color: #e7f3ff;
            border-left: 4px solid #2196F3;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{report_title}</h1>
        {df.to_html(table_id='data-table', classes='table', escape=False, index=False)}
        <div class="info">
            <strong>Data Information:</strong><br>
            Total rows: {len(df)}<br>
            Total columns: {len(df.columns)}<br>
            Source file: {input_path.name}
        </div>
    </div>
</body>
</html>"""

        # Write HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"HTML file created successfully: {output_path}")
        print(f"Converted {len(df)} rows and {len(df.columns)} columns")

        return output_path

    except Exception as e:
        raise Exception(f"Error converting CSV to HTML: {e}")
