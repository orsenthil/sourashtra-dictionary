#!/usr/bin/env python3
"""
Analyze dictpress CSV files for potential constraint violations
"""

import argparse
import csv
from pathlib import Path
from collections import defaultdict

def analyze_file(csv_file: Path):
    """Analyze a single CSV file for constraint violations"""
    print(f"\n=== Analyzing {csv_file.name} ===")
    
    main_entries = []
    definition_entries = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as infile:
            csv_reader = csv.reader(infile)
            for row_num, row in enumerate(csv_reader, 1):
                if len(row) < 4:
                    continue
                    
                entry_type = row[0].strip()
                content = row[2].strip()
                language = row[3].strip()
                
                if entry_type == '-':
                    main_entries.append((row_num, content))
                elif entry_type == '^':
                    definition_entries.append((row_num, content, language))
    
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")
        return
    
    # Check for duplicate main entries (Sourashtra terms)
    main_counts = defaultdict(list)
    for row_num, content in main_entries:
        main_counts[content].append(row_num)
    
    main_duplicates = {k: v for k, v in main_counts.items() if len(v) > 1}
    
    # Check for duplicate definition entries
    def_counts = defaultdict(list)
    for row_num, content, language in definition_entries:
        key = (content, language)
        def_counts[key].append(row_num)
    
    def_duplicates = {k: v for k, v in def_counts.items() if len(v) > 1}
    
    # Report results
    print(f"Main entries: {len(main_entries)}")
    print(f"Definition entries: {len(definition_entries)}")
    
    if main_duplicates:
        print(f"\n⚠ DUPLICATE MAIN ENTRIES ({len(main_duplicates)}):")
        for content, rows in sorted(main_duplicates.items()):
            print(f"  '{content}' appears on lines: {', '.join(map(str, rows))}")
    else:
        print("✓ No duplicate main entries")
    
    if def_duplicates:
        print(f"\n⚠ DUPLICATE DEFINITION ENTRIES ({len(def_duplicates)}):")
        for (content, language), rows in sorted(def_duplicates.items()):
            print(f"  '{content}' ({language}) appears on lines: {', '.join(map(str, rows))}")
    else:
        print("✓ No duplicate definition entries")
    
    if not main_duplicates and not def_duplicates:
        print("✅ File should import without constraint violations")
    else:
        print("❌ File may cause constraint violations during import")

def main():
    parser = argparse.ArgumentParser(
        description='Analyze dictpress CSV files for potential constraint violations'
    )
    
    parser.add_argument('path',
                       help='CSV file or directory to analyze')
    
    args = parser.parse_args()
    
    path = Path(args.path)
    
    if not path.exists():
        print(f"Error: Path not found: {path}")
        return
    
    if path.is_file():
        if path.suffix.lower() == '.csv':
            analyze_file(path)
        else:
            print(f"Error: {path} is not a CSV file")
    elif path.is_dir():
        csv_files = sorted(path.glob("*.csv"))
        if not csv_files:
            print(f"No CSV files found in {path}")
            return
        
        print(f"Analyzing {len(csv_files)} CSV files in {path}")
        
        total_violations = 0
        for csv_file in csv_files:
            analyze_file(csv_file)
            # Simple check - could be enhanced to count actual violations
        
        print(f"\n=== SUMMARY ===")
        print(f"Analyzed {len(csv_files)} files")
    else:
        print(f"Error: {path} is neither a file nor directory")

if __name__ == "__main__":
    main()


