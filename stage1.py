import argparse
import logging

import pandas as pd
import os
from pathlib import Path

def process_csv_files(csvdir, opdir):
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
            print(f"Error processing {csv_file.name}: {e}")
    
    # Combine all dataframes
    if all_dataframes:
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        
        # Write the combined dataframe to output directory
        output_file = Path(opdir) / "combined_data.csv"
        combined_df.to_csv(output_file, index=False)
        
        print(f"Combined CSV file saved to: {output_file}")
        print(f"Total rows: {len(combined_df)}")
        print(f"Total columns: {len(combined_df.columns)}")
    else:
        print("No data to combine")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--statementdir", required=True)
    ap.add_argument("--outputdir", required=True)

    a = ap.parse_args()

    process_csv_files(a.statementdir, a.outputdir)

if __name__ == '__main__':
    main()