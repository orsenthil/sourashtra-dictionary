#!/usr/bin/env python3
"""
Transliterator for Sourashtra Dictionary
This script processes CSV files from the processed directory and adds transliterations
for each Sourashtra word using the aksharamukha library.

Input format:  Sourashtra word, Hindi pronunciation, Tamil pronunciation, English meaning, Tamil meaning
Output format: Sourashtra word, Hindi pronunciation, Tamil pronunciation, RomanReadable, HK, IAST, IPA, English meaning, Tamil meaning

Usage: python3 transliterate.py <processed_directory> [output_directory]
"""

import argparse
import csv
import os
import sys
from pathlib import Path

try:
    from aksharamukha import transliterate
except ImportError:
    print("Error: aksharamukha library not found. Please install it:")
    print("pip install aksharamukha")
    sys.exit(1)


def transliterate_sourashtra_word(sourashtra_word):
    """
    Transliterate a Sourashtra word to multiple formats.
    
    Args:
        sourashtra_word (str): The Sourashtra word to transliterate
        
    Returns:
        dict: Dictionary with transliterations in different formats
    """
    if not sourashtra_word or sourashtra_word.strip() == '':
        return {
            'RomanReadable': '',
            'HK': '',
            'IAST': '',
            'IPA': ''
        }
    
    try:
        # Clean the input word (remove extra spaces)
        clean_word = sourashtra_word.strip()
        
        # Transliterate to different formats
        roman_readable = transliterate.process('Saurashtra', 'RomanReadable', clean_word, nativize=True)
        hk = transliterate.process('Saurashtra', 'HK', clean_word, nativize=True)
        iast = transliterate.process('Saurashtra', 'IAST', clean_word, nativize=True)
        ipa = transliterate.process('Saurashtra', 'IPA', clean_word, nativize=True)
        
        return {
            'RomanReadable': roman_readable or '',
            'HK': hk or '',
            'IAST': iast or '',
            'IPA': ipa or ''
        }
        
    except Exception as e:
        print(f"Warning: Failed to transliterate '{sourashtra_word}': {str(e)}")
        return {
            'RomanReadable': '',
            'HK': '',
            'IAST': '',
            'IPA': ''
        }


def process_csv_line(row):
    """
    Process a single CSV line and add transliterations.
    
    Args:
        row (list): CSV row with 5 columns [Sourashtra, Hindi, Tamil, English, Tamil_meaning]
        
    Returns:
        list: Expanded row with transliterations [Sourashtra, Hindi, Tamil, RomanReadable, HK, IAST, IPA, English, Tamil_meaning]
    """
    if len(row) != 5:
        print(f"Warning: Expected 5 columns, found {len(row)}: {row}")
        return row  # Return as-is if not 5 columns
    
    sourashtra_word, hindi_pronunciation, tamil_pronunciation, english_meaning, tamil_meaning = row
    
    # Get transliterations
    transliterations = transliterate_sourashtra_word(sourashtra_word)
    
    # Create new row with transliterations inserted after Tamil pronunciation
    new_row = [
        sourashtra_word,
        hindi_pronunciation,
        tamil_pronunciation,
        transliterations['RomanReadable'],
        transliterations['HK'],
        transliterations['IAST'],
        transliterations['IPA'],
        english_meaning,
        tamil_meaning
    ]
    
    return new_row


def process_csv_file(input_file, output_file):
    """
    Process a single CSV file by adding transliterations.
    
    Args:
        input_file (Path): Path to input CSV file
        output_file (Path): Path to output CSV file
        
    Returns:
        tuple: (success, error_message, lines_processed)
    """
    try:
        lines_processed = 0
        all_processed_rows = []
        
        # First, read all data and process it
        with open(input_file, 'r', encoding='utf-8') as infile:
            csv_reader = csv.reader(infile)
            
            for row in csv_reader:
                # Skip completely empty rows
                if not row or all(field.strip() == '' for field in row):
                    continue
                
                lines_processed += 1
                
                # Process the row to add transliterations
                processed_row = process_csv_line(row)
                all_processed_rows.append(processed_row)
        
        # Then write all data
        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            csv_writer = csv.writer(outfile, lineterminator='\n')
            for row in all_processed_rows:
                # Clean any carriage returns from the row data
                cleaned_row = [field.replace('\r', '').replace('\n', ' ') if isinstance(field, str) else field for field in row]
                csv_writer.writerow(cleaned_row)
        
        return True, None, lines_processed
        
    except Exception as e:
        return False, f"Error processing file: {str(e)}", 0


def main():
    """Main function to process all CSV files in the specified directory."""
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Add transliterations to processed CSV files using aksharamukha',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Input format (5 columns):
  Sourashtra word, Hindi pronunciation, Tamil pronunciation, English meaning, Tamil meaning

Output format (9 columns):  
  Sourashtra word, Hindi pronunciation, Tamil pronunciation, RomanReadable, HK, IAST, IPA, English meaning, Tamil meaning

Examples:
  python3 transliterate.py processed/
  python3 transliterate.py processed/ transliterated/
  python3 transliterate.py /path/to/processed/ /path/to/output/
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
    print("Adding transliterations: RomanReadable, HK, IAST, IPA")
    print("=" * 80)
    
    # Find all CSV files
    csv_files = sorted(processed_dir.glob('*.csv'))
    
    if not csv_files:
        print("No CSV files found in the directory.")
        return
    
    total_files = len(csv_files)
    processed_files = 0
    total_lines = 0
    
    for csv_file in csv_files:
        # Create output filename
        output_file = output_dir / csv_file.name
        
        print(f"\nProcessing: {csv_file.name}")
        if not overwrite_mode:
            print(f"  → {output_file.name}")
        
        # Process the file
        success, error_msg, lines_processed = process_csv_file(csv_file, output_file)
        
        if success:
            print(f"  ✓ Success - {lines_processed} lines processed with transliterations added")
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
    print("\n" + "=" * 80)
    print("✓ All CSV files processed successfully!")
    print(f"Summary:")
    print(f"Total files processed: {processed_files}")
    print(f"Total lines processed: {total_lines}")
    print(f"Transliterations added: RomanReadable, HK, IAST, IPA")
    print(f"Output directory: {output_dir}")
    print("\nOutput format: Sourashtra, Hindi, Tamil, RomanReadable, HK, IAST, IPA, English, Tamil_meaning")


if __name__ == "__main__":
    main()
