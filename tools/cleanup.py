#!/usr/bin/env python3
"""
CSV Cleanup Tool for Sourashtra Dictionary
This tool removes clarification terms in brackets (like (adj), (noun), (N)) from CSV files.

Usage: python3 cleanup.py <directory_path> [output_directory]
Example: python3 cleanup.py words/
"""

import argparse
import csv
import os
import sys
import re
import tempfile
import shutil
from pathlib import Path
from difflib import unified_diff


def clean_bracket_terms(text):
    """
    Remove all terms in brackets from the given text.
    
    Args:
        text (str): Text that may contain bracketed terms
        
    Returns:
        str: Text with all bracketed terms removed and extra spaces cleaned up
    """
    if not text or not isinstance(text, str):
        return text
    
    # Remove all terms in brackets using regex
    # Pattern matches: ( followed by any characters except ), followed by )
    cleaned_text = re.sub(r'\s*\([^)]*\)\s*', '', text)
    
    # Clean up extra spaces and return
    return ' '.join(cleaned_text.split()).strip()


def process_csv_line(row):
    """
    Process a single CSV line and remove bracket terms from all fields.
    
    Args:
        row (list): CSV row with multiple columns
        
    Returns:
        list: Cleaned row with bracket terms removed from all fields
    """
    if not row:
        return row
    
    # Clean bracket terms from all fields in the row
    cleaned_row = []
    for field in row:
        cleaned_field = clean_bracket_terms(field)
        cleaned_row.append(cleaned_field)
    
    return cleaned_row


def has_bracket_terms(row):
    """
    Check if any field in the row contains bracket terms.
    
    Args:
        row (list): CSV row with multiple columns
        
    Returns:
        bool: True if any field contains bracket terms
    """
    if not row:
        return False
    
    for field in row:
        if isinstance(field, str) and re.search(r'\([^)]*\)', field):
            return True
    return False


def process_csv_file(input_file, output_file, dry_run=False):
    """
    Process a single CSV file by removing bracket terms only from lines that contain them.
    
    Args:
        input_file (Path): Path to input CSV file
        output_file (Path): Path to output CSV file
        dry_run (bool): If True, don't write changes, just return diff info
        
    Returns:
        tuple: (success, error_message, lines_processed, bracket_terms_removed, changes_made, diff_lines)
    """
    try:
        lines_processed = 0
        bracket_terms_removed = 0
        changes_made = []
        original_lines = []
        modified_lines = []
        
        # Read the original file as raw lines for diff generation
        with open(input_file, 'r', encoding='utf-8') as infile:
            original_content = infile.read()
            original_lines = original_content.splitlines(keepends=True)
        
        # Process the file line by line, preserving original formatting
        modified_content_lines = []
        
        # Read raw lines first
        with open(input_file, 'r', encoding='utf-8') as infile:
            raw_lines = infile.readlines()
        
        # Process CSV data
        with open(input_file, 'r', encoding='utf-8') as infile:
            csv_reader = csv.reader(infile)
            csv_rows = list(csv_reader)
        
        # Process each line
        for line_num, (raw_line, csv_row) in enumerate(zip(raw_lines, csv_rows), 1):
            lines_processed += 1
            
            # Skip completely empty rows but preserve them
            if not csv_row or all(field.strip() == '' for field in csv_row):
                modified_content_lines.append(raw_line)
                continue
            
            # Check if this row has bracket terms
            if has_bracket_terms(csv_row):
                # Count bracket terms before removal
                original_text = ''.join(csv_row)
                bracket_matches = re.findall(r'\([^)]*\)', original_text)
                bracket_terms_removed += len(bracket_matches)
                
                # Clean the row
                cleaned_row = process_csv_line(csv_row)
                
                # Generate the cleaned line in CSV format
                import io
                output = io.StringIO()
                writer = csv.writer(output, lineterminator='\n')
                writer.writerow(cleaned_row)
                cleaned_line = output.getvalue()
                
                # Store the change
                changes_made.append({
                    'line_num': line_num,
                    'original': raw_line.rstrip('\n\r'),
                    'modified': cleaned_line.rstrip('\n\r'),
                    'bracket_terms': bracket_matches
                })
                
                modified_content_lines.append(cleaned_line)
            else:
                # No bracket terms, keep original line unchanged
                modified_content_lines.append(raw_line)
        
        # Generate unified diff
        diff_lines = []
        if changes_made:
            diff_lines = list(unified_diff(
                original_lines,
                modified_content_lines,
                fromfile=f'a/{input_file.name}',
                tofile=f'b/{input_file.name}',
                lineterm='',
                n=3  # Context lines
            ))
        
        # Write the file only if not in dry run mode and there are changes
        if not dry_run and changes_made:
            with open(output_file, 'w', encoding='utf-8') as outfile:
                outfile.writelines(modified_content_lines)
        
        return True, None, lines_processed, bracket_terms_removed, changes_made, diff_lines
        
    except Exception as e:
        return False, f"Error processing file: {str(e)}", 0, 0, [], []


def main():
    """Main function to process all CSV files in the specified directory."""
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Remove bracket clarification terms from CSV files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
This tool removes clarification terms in brackets like:
  (adj), (noun), (N), (verb), etc.

Examples:
  python3 cleanup.py words/                    # Clean files in place
  python3 cleanup.py words/ --dry-run          # Preview changes without modifying files
  python3 cleanup.py words/ cleaned_words/     # Output to separate directory
  python3 cleanup.py words/ --no-diff         # Don't show diff output

Before: பிந்தா3  (adj)
After:  பிந்தா3
        '''
    )
    parser.add_argument('directory_path', 
                       help='Path to the directory containing CSV files to clean')
    parser.add_argument('output_directory', 
                       nargs='?', 
                       default=None,
                       help='Path to the output directory (default: overwrite input files)')
    parser.add_argument('--dry-run', '-n',
                       action='store_true',
                       help='Preview changes without modifying files')
    parser.add_argument('--no-diff',
                       action='store_true', 
                       help='Don\'t show diff output')
    parser.add_argument('--diff-only',
                       action='store_true',
                       help='Only show diff output, don\'t show individual line changes')
    
    args = parser.parse_args()
    
    # Convert to Path objects and resolve
    input_dir = Path(args.directory_path).resolve()
    
    if args.output_directory and not args.dry_run:
        output_dir = Path(args.output_directory).resolve()
        overwrite_mode = False
    else:
        output_dir = input_dir
        overwrite_mode = True
    
    # Validate input directory
    if not input_dir.exists():
        print(f"Error: Directory not found at {input_dir}")
        sys.exit(1)
    
    if not input_dir.is_dir():
        print(f"Error: {input_dir} is not a directory")
        sys.exit(1)
    
    # Create output directory if it doesn't exist and we're not overwriting
    if not overwrite_mode and not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Processing CSV files from: {input_dir}")
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
    else:
        print(f"Output directory: {output_dir}")
        if overwrite_mode:
            print("⚠️  WARNING: Files will be overwritten in place!")
    print("Removing bracket terms like: (adj), (noun), (N), (verb), etc.")
    print("=" * 80)
    
    # Find all CSV files
    csv_files = sorted(input_dir.glob('*.csv'))
    
    if not csv_files:
        print("No CSV files found in the directory.")
        return
    
    total_files = len(csv_files)
    processed_files = 0
    total_lines = 0
    total_bracket_terms_removed = 0
    total_changes_made = 0
    
    for csv_file in csv_files:
        # Create output filename
        output_file = output_dir / csv_file.name
        
        print(f"\nProcessing: {csv_file.name}")
        if not overwrite_mode and not args.dry_run:
            print(f"  → {output_file.name}")
        
        # Process the file
        success, error_msg, lines_processed, bracket_terms_removed, changes_made, diff_lines = process_csv_file(
            csv_file, output_file, dry_run=args.dry_run
        )
        
        if success:
            if bracket_terms_removed > 0:
                status = "DRY RUN" if args.dry_run else "Success"
                print(f"  ✓ {status} - {lines_processed} lines processed, {bracket_terms_removed} bracket terms removed from {len(changes_made)} lines")
                
                # Show individual line changes unless diff-only mode
                if not args.diff_only and not args.no_diff:
                    for change in changes_made[:5]:  # Show first 5 changes
                        print(f"    Line {change['line_num']}: Removed {change['bracket_terms']}")
                        print(f"      Before: {change['original']}")
                        print(f"      After:  {change['modified']}")
                    
                    if len(changes_made) > 5:
                        print(f"    ... and {len(changes_made) - 5} more changes")
                
                # Show unified diff if requested and available
                if not args.no_diff and diff_lines:
                    print(f"\n📋 Diff for {csv_file.name}:")
                    for line in diff_lines:
                        print(line)
                    
            else:
                print(f"  ✓ Success - {lines_processed} lines processed, no bracket terms found")
                
            processed_files += 1
            total_lines += lines_processed
            total_bracket_terms_removed += bracket_terms_removed
            total_changes_made += len(changes_made)
            
        else:
            print(f"  ✗ Failed - {error_msg}")
            print(f"  Stopping processing due to error.")
            
            # Print summary before exiting
            print(f"\nSummary:")
            print(f"Files processed: {processed_files} out of {total_files}")
            print(f"Total lines processed: {total_lines}")
            print(f"Total bracket terms removed: {total_bracket_terms_removed}")
            print(f"Total lines changed: {total_changes_made}")
            
            sys.exit(1)
    
    # All files processed successfully
    print("\n" + "=" * 80)
    mode_msg = "✓ All CSV files analyzed!" if args.dry_run else "✓ All CSV files processed successfully!"
    print(mode_msg)
    print(f"Summary:")
    print(f"Total files processed: {processed_files}")
    print(f"Total lines processed: {total_lines}")
    print(f"Total bracket terms removed: {total_bracket_terms_removed}")
    print(f"Total lines changed: {total_changes_made}")
    if not args.dry_run:
        print(f"Output directory: {output_dir}")
    
    if total_bracket_terms_removed > 0:
        if args.dry_run:
            print(f"\n🔍 Analysis complete! Found {total_bracket_terms_removed} bracket terms in {total_changes_made} lines that would be cleaned.")
            print("Run without --dry-run to apply changes.")
        else:
            print(f"\n🧹 Cleanup complete! Removed {total_bracket_terms_removed} clarification terms from {total_changes_made} lines.")
    else:
        print(f"\n✨ Files are already clean! No bracket terms found to remove.")


if __name__ == "__main__":
    main()
