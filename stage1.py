import argparse
import logging

import pandas as pd
import os
from pathlib import Path

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

    return output_filename

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

    stage1_opfile = process_csv_files_stage1(a.statementdir, a.outputdir)
    stage2_opfile = remove_columns_from_csv(stage1_opfile, DEL_COLUMN_LIST,  a.outputdir)

if __name__ == '__main__':
    main()