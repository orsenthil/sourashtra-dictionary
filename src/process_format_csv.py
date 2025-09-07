#!/usr/bin/env python3
"""
CSV Processor for Sourashtra Dictionary
This script processes CSV files from the csv directory by reversing column order (c1,c2,c3,c4,c5 -> c5,c4,c3,c2,c1)
and saves them with simplified names in the processed directory.

Input: Sourashtra-CIIL-List-Original_[SUBJECT].csv
Output: processed/[SUBJECT].csv

Usage: python3 process_format_csv.py <csv_directory> [processed_directory]
"""

import argparse
import csv
import os
import sys
from pathlib import Path
import re


def extract_subject_from_filename(filename):
    """
    Extract the subject name from the original filename.
    
    Args:
        filename (str): Original filename like 'Sourashtra-CIIL-List-Original_Adjectives.csv'
        
    Returns:
        str: Subject name like 'Adjectives' or None if pattern doesn't match
    """
    # Match pattern: Sourashtra-CIIL-List-Original_[SUBJECT].csv
    pattern = r'Sourashtra-CIIL-List-Original_(.+)\.csv$'
    match = re.match(pattern, filename)
    
    if match:
        return match.group(1)
    return None


def process_csv_file(input_file, output_file):
    """
    Process a single CSV file by reversing the column order.
    
    Args:
        input_file (Path): Path to input CSV file
        output_file (Path): Path to output CSV file
        
    Returns:
        tuple: (success, error_message, lines_processed)
    """
    try:
        lines_processed = 0
        
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            
            csv_reader = csv.reader(infile)
            csv_writer = csv.writer(outfile)
            
            for row in csv_reader:
                # Skip empty rows
                if not any(field.strip() for field in row):
                    continue
                
                # Ensure we have exactly 5 columns
                if len(row) != 5:
                    return False, f"Line {lines_processed + 1}: Expected 5 columns, found {len(row)}", lines_processed
                
                # Reverse the column order: c1,c2,c3,c4,c5 -> c5,c4,c3,c2,c1
                reversed_row = [row[4], row[3], row[2], row[1], row[0]]
                
                csv_writer.writerow(reversed_row)
                lines_processed += 1
        
        return True, None, lines_processed
        
    except Exception as e:
        return False, f"Error processing file: {str(e)}", 0


def main():
    """Main function to process all CSV files in the specified directory."""
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Process CSV files by reversing column order and renaming',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python3 process_format_csv.py csv/
  python3 process_format_csv.py csv/ processed/
  python3 process_format_csv.py /path/to/csv/ /path/to/output/
        '''
    )
    parser.add_argument('csv_directory', 
                       help='Path to the directory containing input CSV files')
    parser.add_argument('processed_directory', 
                       nargs='?', 
                       default='processed',
                       help='Path to the output directory (default: processed)')
    
    args = parser.parse_args()
    
    # Convert to Path objects and resolve
    csv_dir = Path(args.csv_directory).resolve()
    processed_dir = Path(args.processed_directory).resolve()
    
    # Validate input directory
    if not csv_dir.exists():
        print(f"Error: CSV directory not found at {csv_dir}")
        sys.exit(1)
    
    if not csv_dir.is_dir():
        print(f"Error: {csv_dir} is not a directory")
        sys.exit(1)
    
    # Create processed directory if it doesn't exist
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Processing CSV files from: {csv_dir}")
    print(f"Output directory: {processed_dir}")
    print("=" * 70)
    
    # Find all matching CSV files
    pattern = "Sourashtra-CIIL-List-Original_*.csv"
    csv_files = sorted(csv_dir.glob(pattern))
    
    if not csv_files:
        print(f"No CSV files matching pattern '{pattern}' found in the directory.")
        return
    
    total_files = len(csv_files)
    processed_files = 0
    total_lines = 0
    
    for csv_file in csv_files:
        # Extract subject name
        subject = extract_subject_from_filename(csv_file.name)
        
        if not subject:
            print(f"⚠️  Skipping {csv_file.name} - doesn't match expected pattern")
            continue
        
        # Create output filename
        output_filename = f"{subject}.csv"
        output_file = processed_dir / output_filename
        
        print(f"\nProcessing: {csv_file.name}")
        print(f"  → {output_filename}")
        
        # Process the file
        success, error_msg, lines_processed = process_csv_file(csv_file, output_file)
        
        if success:
            print(f"  ✓ Success - {lines_processed} lines processed")
            processed_files += 1
            total_lines += lines_processed
        else:
            print(f"  ✗ Failed - {error_msg}")
            print(f"  Stopping processing due to error.")
            
            # Print summary before exiting
            print(f"\nSummary:")
            print(f"Files processed: {processed_files} out of {total_files}")
            print(f"Total lines processed: {total_lines}")
            
            sys.exit(1)
    
    # All files processed successfully
    print("\n" + "=" * 70)
    print("✓ All CSV files processed successfully!")
    print(f"Summary:")
    print(f"Total files processed: {processed_files}")
    print(f"Total lines processed: {total_lines}")
    print(f"Output directory: {processed_dir}")


if __name__ == "__main__":
    main()
