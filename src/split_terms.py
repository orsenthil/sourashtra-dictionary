#!/usr/bin/env python3
"""
Term Splitter for Sourashtra Dictionary
This script splits composite terms in processed CSV files where columns c1, c2, c3 
contain multiple terms separated by '/' or ',' characters.

For composite terms like:
a1/a2, b1/b2, c1/c2, d1, e1

It creates separate lines:
a1, b1, c1, d1, e1
a2, b2, c2, d1, e1

Usage: python3 split_terms.py <processed_directory> [output_directory]
"""

import argparse
import csv
import os
import sys
from pathlib import Path
import re


def split_field_by_separators(field):
    """
    Split a field by '/' or ',' separators, handling quoted content properly.
    
    Args:
        field (str): Field content that may contain composite terms
        
    Returns:
        list: List of individual terms
    """
    if not field or field.strip() == '':
        return ['']
    
    # Handle cases where the entire field is quoted
    field = field.strip()
    if field.startswith('"') and field.endswith('"'):
        # Remove outer quotes and split the inner content
        inner_content = field[1:-1]
        # Split by comma first, then by forward slash
        parts = []
        for part in inner_content.split(','):
            part = part.strip()
            if '/' in part:
                parts.extend([p.strip() for p in part.split('/')])
            else:
                parts.append(part)
        return parts
    else:
        # Split by forward slash, then by comma
        parts = []
        for part in field.split('/'):
            part = part.strip()
            if ',' in part:
                parts.extend([p.strip() for p in part.split(',')])
            else:
                parts.append(part)
        return parts


def process_csv_line(row):
    """
    Process a single CSV line and split composite terms in c1, c2, c3.
    
    Args:
        row (list): CSV row with 5 columns
        
    Returns:
        list: List of expanded rows with individual terms
    """
    if len(row) != 5:
        return [row]  # Return as-is if not 5 columns
    
    c1, c2, c3, c4, c5 = row
    
    # Split the first three columns
    c1_terms = split_field_by_separators(c1)
    c2_terms = split_field_by_separators(c2)
    c3_terms = split_field_by_separators(c3)
    
    # Find the maximum number of terms across c1, c2, c3
    max_terms = max(len(c1_terms), len(c2_terms), len(c3_terms))
    
    # If all columns have only one term, return the original row
    if max_terms == 1:
        return [row]
    
    # Pad shorter lists with their last element (or empty string if empty)
    def pad_list(lst, target_length):
        if not lst:
            return [''] * target_length
        while len(lst) < target_length:
            lst.append(lst[-1] if lst else '')
        return lst
    
    c1_terms = pad_list(c1_terms, max_terms)
    c2_terms = pad_list(c2_terms, max_terms)
    c3_terms = pad_list(c3_terms, max_terms)
    
    # Create individual rows for each term combination
    result_rows = []
    for i in range(max_terms):
        new_row = [c1_terms[i], c2_terms[i], c3_terms[i], c4, c5]
        result_rows.append(new_row)
    
    return result_rows


def process_csv_file(input_file, output_file):
    """
    Process a single CSV file by splitting composite terms.
    
    Args:
        input_file (Path): Path to input CSV file
        output_file (Path): Path to output CSV file
        
    Returns:
        tuple: (success, error_message, original_lines, expanded_lines)
    """
    try:
        original_lines = 0
        expanded_lines = 0
        all_expanded_rows = []
        
        # First, read all data
        with open(input_file, 'r', encoding='utf-8') as infile:
            csv_reader = csv.reader(infile)
            
            for row in csv_reader:
                # Skip completely empty rows
                if not row or all(field.strip() == '' for field in row):
                    continue
                
                original_lines += 1
                
                # Process the row to split composite terms
                expanded_rows = process_csv_line(row)
                
                # Add all expanded rows to our collection
                for expanded_row in expanded_rows:
                    all_expanded_rows.append(expanded_row)
                    expanded_lines += 1
        
        # Then write all data
        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            csv_writer = csv.writer(outfile, lineterminator='\n')
            for row in all_expanded_rows:
                # Clean any carriage returns from the row data
                cleaned_row = [field.replace('\r', '').replace('\n', ' ') if isinstance(field, str) else field for field in row]
                csv_writer.writerow(cleaned_row)
        
        return True, None, original_lines, expanded_lines
        
    except Exception as e:
        return False, f"Error processing file: {str(e)}", 0, 0


def main():
    """Main function to process all CSV files in the specified directory."""
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Split composite terms in processed CSV files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python3 split_terms.py processed/
  python3 split_terms.py processed/ split_output/
  python3 split_terms.py /path/to/processed/ /path/to/output/
        '''
    )
    parser.add_argument('processed_directory', 
                       help='Path to the directory containing processed CSV files')
    parser.add_argument('output_directory', 
                       nargs='?', 
                       default=None,
                       help='Path to the output directory (default: overwrite input files)')
    
    args = parser.parse_args()
    
    # Convert to Path objects and resolve
    processed_dir = Path(args.processed_directory).resolve()
    
    if args.output_directory:
        output_dir = Path(args.output_directory).resolve()
        overwrite_mode = False
    else:
        output_dir = processed_dir
        overwrite_mode = True
    
    # Validate input directory
    if not processed_dir.exists():
        print(f"Error: Processed directory not found at {processed_dir}")
        sys.exit(1)
    
    if not processed_dir.is_dir():
        print(f"Error: {processed_dir} is not a directory")
        sys.exit(1)
    
    # Create output directory if it doesn't exist and we're not overwriting
    if not overwrite_mode:
        output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Processing CSV files from: {processed_dir}")
    print(f"Output directory: {output_dir}")
    if overwrite_mode:
        print("⚠️  WARNING: Files will be overwritten in place!")
    print("=" * 70)
    
    # Find all CSV files
    csv_files = sorted(processed_dir.glob('*.csv'))
    
    if not csv_files:
        print("No CSV files found in the directory.")
        return
    
    total_files = len(csv_files)
    processed_files = 0
    total_original_lines = 0
    total_expanded_lines = 0
    
    for csv_file in csv_files:
        # Create output filename
        output_file = output_dir / csv_file.name
        
        print(f"\nProcessing: {csv_file.name}")
        if not overwrite_mode:
            print(f"  → {output_file.name}")
        
        # Process the file
        success, error_msg, original_lines, expanded_lines = process_csv_file(csv_file, output_file)
        
        if success:
            expansion_info = ""
            if expanded_lines > original_lines:
                expansion_info = f" (expanded from {original_lines} to {expanded_lines} lines)"
            elif expanded_lines == original_lines:
                expansion_info = f" (no composite terms found)"
            
            print(f"  ✓ Success - {expanded_lines} lines written{expansion_info}")
            processed_files += 1
            total_original_lines += original_lines
            total_expanded_lines += expanded_lines
        else:
            print(f"  ✗ Failed - {error_msg}")
            print(f"  Stopping processing due to error.")
            
            # Print summary before exiting
            print(f"\nSummary:")
            print(f"Files processed: {processed_files} out of {total_files}")
            print(f"Total original lines: {total_original_lines}")
            print(f"Total expanded lines: {total_expanded_lines}")
            
            sys.exit(1)
    
    # All files processed successfully
    print("\n" + "=" * 70)
    print("✓ All CSV files processed successfully!")
    print(f"Summary:")
    print(f"Total files processed: {processed_files}")
    print(f"Total original lines: {total_original_lines}")
    print(f"Total expanded lines: {total_expanded_lines}")
    if total_expanded_lines > total_original_lines:
        print(f"Lines added due to term splitting: {total_expanded_lines - total_original_lines}")
    print(f"Output directory: {output_dir}")


if __name__ == "__main__":
    main()
