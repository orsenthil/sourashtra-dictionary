#!/usr/bin/env python3
"""
CSV File Validator for Sourashtra Dictionary
This script checks all CSV files in a specified directory to ensure they have exactly 5 fields per line.
If a line doesn't have exactly 5 fields, it stops and prints that line.

Usage: python3 check_csv_files.py <csv_directory>
"""

import argparse
import csv
import os
import sys
from pathlib import Path


def check_csv_file(file_path):
    """
    Check if a CSV file has exactly 5 fields per line.
    
    Args:
        file_path (Path): Path to the CSV file
        
    Returns:
        tuple: (is_valid, error_info) where error_info contains line number and content if invalid
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            
            for line_num, row in enumerate(csv_reader, start=1):
                # Skip empty lines
                if not any(field.strip() for field in row):
                    continue
                    
                if len(row) != 5:
                    return False, {
                        'line_number': line_num,
                        'field_count': len(row),
                        'line_content': ','.join(row),
                        'raw_line': file.readline() if hasattr(file, 'readline') else str(row)
                    }
        
        return True, None
        
    except Exception as e:
        return False, {
            'line_number': 0,
            'field_count': 0,
            'line_content': f"Error reading file: {str(e)}",
            'raw_line': ''
        }


def main():
    """Main function to check all CSV files in the specified directory."""
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Check CSV files for exactly 5 fields per line',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python3 check_csv_files.py csv/
  python3 check_csv_files.py /path/to/csv/directory/
        '''
    )
    parser.add_argument('csv_directory', 
                       help='Path to the directory containing CSV files to check')
    
    args = parser.parse_args()
    
    # Convert to Path object and resolve
    csv_dir = Path(args.csv_directory).resolve()
    
    if not csv_dir.exists():
        print(f"Error: CSV directory not found at {csv_dir}")
        sys.exit(1)
    
    if not csv_dir.is_dir():
        print(f"Error: {csv_dir} is not a directory")
        sys.exit(1)
    
    print(f"Checking CSV files in: {csv_dir}")
    print("=" * 60)
    
    # Get all CSV files
    csv_files = sorted(csv_dir.glob('*.csv'))
    
    if not csv_files:
        print("No CSV files found in the directory.")
        return
    
    total_files = len(csv_files)
    valid_files = 0
    
    for csv_file in csv_files:
        print(f"\nChecking: {csv_file.name}")
        
        is_valid, error_info = check_csv_file(csv_file)
        
        if is_valid:
            print("✓ Valid - All lines have exactly 5 fields")
            valid_files += 1
        else:
            print("✗ Invalid CSV file found!")
            print(f"File: {csv_file.name}")
            print(f"Line {error_info['line_number']}: Found {error_info['field_count']} fields instead of 5")
            print(f"Line content: {error_info['line_content']}")
            print("\nStopping validation as requested.")
            
            # Print summary before exiting
            print(f"\nSummary:")
            print(f"Files checked: {csv_files.index(csv_file) + 1} out of {total_files}")
            print(f"Valid files: {valid_files}")
            print(f"Invalid files: 1 (stopped at first invalid file)")
            
            sys.exit(1)
    
    # All files are valid
    print("\n" + "=" * 60)
    print("✓ All CSV files are valid!")
    print(f"Summary:")
    print(f"Total files checked: {total_files}")
    print(f"All files have exactly 5 fields per line.")


if __name__ == "__main__":
    main()
