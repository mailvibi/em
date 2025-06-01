import argparse
import logging
import json

import pandas as pd
import os
from pathlib import Path

def csv_to_html(csv_filename, output_directory=None):
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

        # Determine output directory
        input_path = Path(csv_filename)
        if output_directory is None:
            output_dir = input_path.parent
        else:
            output_dir = Path(output_directory)
            os.makedirs(output_dir, exist_ok=True)

        # Create output filename
        output_filename = f"{input_path.stem}.html"
        output_path = output_dir / output_filename

        # Create HTML content with styling
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{input_path.stem} - CSV Data</title>
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
        <h1>CSV Data: {input_path.name}</h1>
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


def process_csv_files_stage1(csvdir, opdir):
    """
    Read CSV files from csvdir, add csvfilename column, combine all files,
    and write the combined result to opdir.
    
    Args:
        csvdir (str): Directory containing CSV files
        opdir (str): Output directory for the combined CSV file
    """
    # Create output directory if it doesn't exist
    os.makedirs(opdir, exist_ok=True)
    
    # List to store all dataframes
    all_dataframes = []
    
    # Get all CSV files from the input directory
    csv_files = list(Path(csvdir).glob("*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {csvdir}")
        return
    
    # Process each CSV file
    for csv_file in csv_files:
        try:
            # Read the CSV file
            df = pd.read_csv(csv_file)
            
            # Add the csvfilename column with the filename (without extension)
            df['csvfilename'] = csv_file.stem
            
            # Add to the list of dataframes
            all_dataframes.append(df)
            print(f"Processed: {csv_file.name}")
            
        except Exception as e:
            raise Exception(f"Error processing {csv_file.name}: {e}")
            print(f"Error processing {csv_file.name}: {e}")
    
    # Combine all dataframes
    if all_dataframes:
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        
        # Write the combined dataframe to output directory
        output_file = Path(opdir) / "stage1_combined_data.csv"
        combined_df.to_csv(output_file, index=False)
        
        print(f"Combined CSV file saved to: {output_file}")
        print(f"Total rows: {len(combined_df)}")
        print(f"Total columns: {len(combined_df.columns)}")
        return output_file
    else:
        print("No data to combine")
        raise Exception("No data to combine to csv file")

def remove_columns_from_csv(csv_file_path, columns_to_remove, output_directory):
    """
    Remove specified columns from a CSV file and save the result to an output directory.

    Args:
        csv_file_path (str): Path to the input CSV file
        columns_to_remove (list): List of column names to remove
        output_directory (str): Directory where the modified CSV will be saved

    Returns:
        str: Name of the output file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Read the CSV file
    df = pd.read_csv(csv_file_path)

    # Get the original filename
    input_file = Path(csv_file_path)
    original_filename = input_file.stem

    # Remove columns that exist in the dataframe
    columns_to_drop = [col for col in columns_to_remove if col in df.columns]

    if columns_to_drop:
        df_modified = df.drop(columns=columns_to_drop)
        print(f"Removed columns: {columns_to_drop}")
    else:
        df_modified = df.copy()
        print("No matching columns found to remove")

    # Create output filename
    output_filename = f"stage2_{original_filename}_modified.csv"
    output_path = Path(output_directory) / output_filename

    # Save the modified dataframe
    df_modified.to_csv(output_path, index=False)

    print(f"Modified CSV saved to: {output_path}")
    print(f"Original columns: {len(df.columns)}, Remaining columns: {len(df_modified.columns)}")

    return output_path


def reverse_map_json(json_filename):
    """
    Read a JSON file and return a dictionary with reversed key-value mapping.

    Args:
        json_filename (str): Path to the JSON file

    Returns:
        dict: Dictionary with keys and values swapped from the original

    Raises:
        Exception: For any errors during file reading or processing
    """
    try:
        # Read the JSON file
        with open(json_filename, 'r', encoding='utf-8') as file:
            original_dict = json.load(file)

        # Validate that the loaded content is a dictionary
        if not isinstance(original_dict, dict):
            raise ValueError("JSON file must contain a dictionary at the root level")

        # Create reverse mapping dictionary
        reversed_dict = {}
        for key, value in original_dict.items():
            # Check if value is hashable (can be used as a key)
            for v in value:
                try:
                    hash(v)
                    reversed_dict[v] = key
                except TypeError:
                    raise ValueError(f"Value '{v}' for key '{key}' is not hashable and cannot be used as a dictionary key")

        return reversed_dict

    except FileNotFoundError:
        raise Exception(f"JSON file '{json_filename}' not found")
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON format in file '{json_filename}': {e}")
    except Exception as e:
        raise Exception(f"Error processing JSON file '{json_filename}': {e}")


def categorize_csv_data(csv_filename, column_name, mapping_dict, output_directory):
    """
    Read a CSV file, match column values against dictionary keys, add CATAGORY column,
    and save the result to output directory.

    Args:
        csv_filename (str): Path to the input CSV file
        column_name (str): Name of the column to check for matches
        mapping_dict (dict): Dictionary with keys to match against
        output_directory (str): Directory where the output CSV will be saved

    Returns:
        str: Path to the output file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Read the CSV file
    df = pd.read_csv(csv_filename)

    # Check if the specified column exists
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in CSV file")

    # Create the CATAGORY column
    df['CATAGORY'] = ''

    # Process each row
    for index, row in df.iterrows():
        cell_value = str(row[column_name])
        
        # Check if any dictionary key matches the cell value
        for key, value in mapping_dict.items():
            if str(key) in cell_value:
                df.at[index, 'CATAGORY'] = value
                break
        if df.at[index, 'CATAGORY'] == "":
            df.at[index, 'CATAGORY'] = "NO CATEGORY"
    # Create output filename
    input_file = Path(csv_filename)
    output_filename = f"{input_file.stem}_categorized.csv"
    output_path = Path(output_directory) / output_filename

    # Save the modified dataframe
    df.to_csv(output_path, index=False)

    print(f"Categorized CSV saved to: {output_path}")
    print(f"Total rows processed: {len(df)}")
    
    return str(output_path)


def filter_and_convert_csv(csv_filename, column_name, output_directory):
    """
    Process CSV file by removing rows with positive values in specified column
    or converting negative values to positive, then save to output directory.

    Args:
        csv_filename (str): Path to the input CSV file
        column_name (str): Name of the column to check for positive/negative values
        output_directory (str): Directory where the processed CSV will be saved

    Returns:
        str: Filename of the newly created CSV file

    Raises:
        Exception: For file not found, column not found, or other processing errors
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_directory, exist_ok=True)

        # Read the CSV file
        try:
            df = pd.read_csv(csv_filename)
        except FileNotFoundError:
            raise Exception(f"CSV file '{csv_filename}' not found")
        except pd.errors.EmptyDataError:
            raise Exception(f"CSV file '{csv_filename}' is empty")
        except Exception as e:
            raise Exception(f"Error reading CSV file '{csv_filename}': {e}")

        # Check if the specified column exists
        if column_name not in df.columns:
            raise Exception(f"Column '{column_name}' not found in CSV file")

        # Convert column to numeric, handling non-numeric values
        try:
            df[column_name] = pd.to_numeric(df[column_name], errors='coerce')
        except Exception as e:
            raise Exception(f"Error converting column '{column_name}' to numeric: {e}")

        # Check for NaN values after conversion
        if df[column_name].isna().any():
            raise Exception(f"Column '{column_name}' contains non-numeric values that cannot be processed")

        # Create a mask for rows to keep (negative values) and convert them to positive
        negative_mask = df[column_name] < 0

        # Filter dataframe to keep only rows with negative values
        df_filtered = df[negative_mask].copy()

        # Convert negative values to positive
        df_filtered[column_name] = df_filtered[column_name].abs()

        # Check if any rows remain after filtering
        if df_filtered.empty:
            print(f"Warning: No negative values found in column '{column_name}'. Output file will be empty.")

        # Create output filename
        input_file = Path(csv_filename)
        output_filename = f"{input_file.stem}_filtered.csv"
        output_path = Path(output_directory) / output_filename

        # Save the filtered dataframe
        df_filtered.to_csv(output_path, index=False)

        print(f"Processed CSV saved to: {output_path}")
        print(f"Original rows: {len(df)}, Remaining rows: {len(df_filtered)}")

        return output_path

    except Exception as e:
        raise Exception(f"Error processing CSV file: {e}")


def sum_amounts_by_category(csv_filename, output_directory):
    """
    Calculate sum of values in 'Amount (EUR)' column grouped by 'CATAGORY' column
    and save the results as a CSV file.

    Args:
        csv_filename (str): Path to the input CSV file
        output_directory (str): Directory where the summary CSV will be saved

    Returns:
        str: Filename of the newly created CSV file

    Raises:
        Exception: For file not found, column not found, or other processing errors
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_directory, exist_ok=True)

        # Read the CSV file
        try:
            df = pd.read_csv(csv_filename)
        except FileNotFoundError:
            raise Exception(f"CSV file '{csv_filename}' not found")
        except pd.errors.EmptyDataError:
            raise Exception(f"CSV file '{csv_filename}' is empty")
        except Exception as e:
            raise Exception(f"Error reading CSV file '{csv_filename}': {e}")

        # Check if required columns exist
        required_columns = ['Amount (EUR)', 'CATAGORY']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise Exception(f"Required columns not found: {missing_columns}")

        # Convert Amount (EUR) column to numeric, handling non-numeric values
        try:
            df['Amount (EUR)'] = pd.to_numeric(df['Amount (EUR)'], errors='coerce')
        except Exception as e:
            raise Exception(f"Error converting 'Amount (EUR)' column to numeric: {e}")

        # Remove rows where Amount (EUR) is NaN after conversion
        original_rows = len(df)
        df = df.dropna(subset=['Amount (EUR)'])
        if len(df) < original_rows:
            print(f"Warning: Removed {original_rows - len(df)} rows with non-numeric 'Amount (EUR)' values")

        # Group by CATAGORY and sum the Amount (EUR)
        summary_df = df.groupby('CATAGORY')['Amount (EUR)'].sum().reset_index()
        summary_df.columns = ['CATAGORY', 'Total Amount (EUR)']

        # Sort by total amount in descending order
        summary_df = summary_df.sort_values('Total Amount (EUR)', ascending=False)

        # Create output filename
        input_file = Path(csv_filename)
        output_filename = f"{input_file.stem}_category_summary.csv"
        output_path = Path(output_directory) / output_filename

        # Save the summary dataframe
        summary_df.to_csv(output_path, index=False)

        print(f"Category summary saved to: {output_path}")
        print(f"Total categories: {len(summary_df)}")
        print(f"Grand total: {summary_df['Total Amount (EUR)'].sum():.2f} EUR")

        return output_path

    except Exception as e:
        raise Exception(f"Error processing CSV file: {e}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--statementdir", required=True)
    ap.add_argument("--outputdir", required=True)

    a = ap.parse_args()

    DEL_COLUMN_LIST = [
        "Value Date",
        "Partner Iban",
        "Type",
        "Payment Reference",
        "Account Name",
        "Original Amount",
        "Original Currency",
        "Exchange Rate",
    ]
    ITEM_TO_CATAGORY_MAP_FILE = "shopname_category_mapping.json"

    stage1_opfile = process_csv_files_stage1(a.statementdir, a.outputdir)
    stage2_opfile = remove_columns_from_csv(stage1_opfile, DEL_COLUMN_LIST,  a.outputdir)
    item_map = reverse_map_json(ITEM_TO_CATAGORY_MAP_FILE)
    stage3_opfile = categorize_csv_data(stage2_opfile, "Partner Name", item_map, a.outputdir)
    stage4_opfile = filter_and_convert_csv(stage3_opfile, "Amount (EUR)", a.outputdir)
    stage5_opfile = sum_amounts_by_category(stage4_opfile, a.outputdir)
    csv_to_html(stage5_opfile)
#    print(item_map)

if __name__ == '__main__':
    main()