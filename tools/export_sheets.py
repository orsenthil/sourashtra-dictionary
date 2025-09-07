import pandas as pd
import os
import sys

def export_all_sheets_to_csv(ods_file_path, output_directory="."):
    """
    Export all sheets from an ODS file to separate CSV files
    """
    try:
        # Read all sheets from ODS file
        all_sheets = pd.read_excel(ods_file_path, sheet_name=None, engine='odf')
        
        # Get base filename without extension
        base_name = os.path.splitext(os.path.basename(ods_file_path))[0]
        
        print(f"Found {len(all_sheets)} sheets in {ods_file_path}")
        
        # Export each sheet to CSV
        for sheet_name, df in all_sheets.items():
            # Create filename: basename_sheetname.csv
            csv_filename = f"{base_name}_{sheet_name}.csv"
            csv_path = os.path.join(output_directory, csv_filename)
            
            # Export to CSV with UTF-8 encoding (important for multilingual content)
            df.to_csv(csv_path, index=False, encoding='utf-8')
            print(f"✓ Exported: '{sheet_name}' -> {csv_filename} ({len(df)} rows)")
        
        print(f"\nAll sheets exported to: {os.path.abspath(output_directory)}")
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python export_sheets.py <ods_file> [output_directory]")
        sys.exit(1)
    
    ods_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    
    export_all_sheets_to_csv(ods_file, output_dir)
