#!/bin/bash
"""
Dictpress CSV Importer Script
This script imports all CSV files from a directory using the dictpress import command.

Usage: ./importer.sh <directory_path>
Example: ./importer.sh dictpress/
"""

# Check if directory argument is provided
if [ $# -eq 0 ]; then
    echo "Error: No directory specified"
    echo "Usage: $0 <directory_path>"
    echo "Example: $0 dictpress/"
    exit 1
fi

# Get the directory path
IMPORT_DIR="$1"

# Check if directory exists
if [ ! -d "$IMPORT_DIR" ]; then
    echo "Error: Directory '$IMPORT_DIR' does not exist"
    exit 1
fi

# Convert to absolute path
IMPORT_DIR=$(realpath "$IMPORT_DIR")

echo "Starting import from directory: $IMPORT_DIR"
echo "=" * 60

# Initialize counters
total_files=0
successful_imports=0
failed_imports=0

# Process each CSV file in the directory
for csv_file in "$IMPORT_DIR"/*.csv; do
    # Check if any CSV files exist
    if [ ! -e "$csv_file" ]; then
        echo "No CSV files found in directory: $IMPORT_DIR"
        exit 0
    fi
    
    # Get just the filename for display
    filename=$(basename "$csv_file")
    
    echo ""
    echo "Importing: $filename"
    echo "File path: $csv_file"
    
    # Increment total files counter
    ((total_files++))
    
    # Run the dictpress import command
    if ./dictpress import --file="$csv_file"; then
        echo "✓ Successfully imported: $filename"
        ((successful_imports++))
    else
        echo "✗ Failed to import: $filename"
        ((failed_imports++))
        
        # Ask user if they want to continue on failure
        echo -n "Continue with remaining files? (y/n): "
        read -r continue_choice
        if [[ ! "$continue_choice" =~ ^[Yy]$ ]]; then
            echo "Import process aborted by user."
            break
        fi
    fi
    
    echo "-" * 40
done

# Print summary
echo ""
echo "=" * 60
echo "IMPORT SUMMARY"
echo "=" * 60
echo "Directory: $IMPORT_DIR"
echo "Total files processed: $total_files"
echo "Successful imports: $successful_imports"
echo "Failed imports: $failed_imports"

if [ $failed_imports -eq 0 ]; then
    echo "🎉 All imports completed successfully!"
    exit 0
else
    echo "⚠️  Some imports failed. Check the output above for details."
    exit 1
fi
