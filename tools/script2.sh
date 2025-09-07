#!/bin/bash
#
# CSV Header Addition Script for Sourashtra Dictionary
# This script adds a header line to each CSV file in the specified directory.
#
# Usage: ./script2.sh <directory_path>
# Example: ./script2.sh processed/
#

# Function to display usage
usage() {
    echo "Usage: $0 <directory_path>"
    echo "Example: $0 processed/"
    echo ""
    echo "This script adds a header line to each CSV file in the specified directory."
    echo "Header: Sourashtra Word, Hindi Pronunciation, Tamil Pronunciation, Roman Readable, Havard-Kyoto, IAST, IPA, Meaning English, Meaning Tamil"
    exit 1
}

# Check if directory argument is provided
if [ $# -eq 0 ]; then
    echo "Error: No directory specified."
    usage
fi

# Get the directory path
DIRECTORY="$1"

# Check if the directory exists
if [ ! -d "$DIRECTORY" ]; then
    echo "Error: Directory '$DIRECTORY' does not exist."
    exit 1
fi

# Define the header line
HEADER="Sourashtra Word,Hindi Pronunciation,Tamil Pronunciation,Roman Readable,Havard-Kyoto,IAST,IPA,Meaning English,Meaning Tamil"

# Counter for processed files
processed_count=0
total_count=0

echo "Adding headers to CSV files in directory: $DIRECTORY"
echo "Header: $HEADER"
echo "=================================================="

# Process each CSV file in the directory
for file in "$DIRECTORY"/*.csv; do
    # Check if any CSV files exist
    if [ ! -e "$file" ]; then
        echo "No CSV files found in directory '$DIRECTORY'"
        exit 1
    fi
    
    total_count=$((total_count + 1))
    filename=$(basename "$file")
    
    echo -n "Processing: $filename ... "
    
    # Check if file already has a header (simple check - if first line contains "Sourashtra Word")
    first_line=$(head -n 1 "$file")
    if [[ "$first_line" == *"Sourashtra Word"* ]]; then
        echo "SKIPPED (header already exists)"
        continue
    fi
    
    # Create a temporary file
    temp_file=$(mktemp)
    
    # Add header to temporary file
    echo "$HEADER" > "$temp_file"
    
    # Append original content to temporary file
    cat "$file" >> "$temp_file"
    
    # Replace original file with temporary file
    if mv "$temp_file" "$file"; then
        processed_count=$((processed_count + 1))
        echo "SUCCESS"
    else
        echo "FAILED"
        rm -f "$temp_file"
    fi
done

echo "=================================================="
echo "Summary:"
echo "Total CSV files found: $total_count"
echo "Files processed (headers added): $processed_count"
echo "Files skipped (headers already exist): $((total_count - processed_count))"

if [ $processed_count -gt 0 ]; then
    echo ""
    echo "✓ Headers successfully added to $processed_count files!"
    echo "Each file now has the header:"
    echo "$HEADER"
else
    echo ""
    echo "ℹ No files needed header addition."
fi
