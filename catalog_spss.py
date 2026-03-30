#!/usr/bin/env python3
"""
Standalone SPSS Cataloger Script

Usage:
    python catalog_spss.py /path/to/spss/files [output_file.csv]

Example:
    python catalog_spss.py /mnt/nsdata1/MainstageR8 catalog_output.csv
"""

import sys
import os

# Add src directory to path to import cataloger
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from spss_cataloger import SpssDirectoryCataloger


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    directory = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'spss_catalog.csv'
    
    # Validate input directory
    if not os.path.isdir(directory):
        print(f"❌ Error: Directory not found: {directory}")
        sys.exit(1)
    
    print(f"🔍 Scanning: {directory}")
    print(f"📝 Output will be saved to: {output_file}\n")
    
    try:
        cataloger = SpssDirectoryCataloger()
        cataloger.catalog_directory(directory, recursive=True)
        cataloger.save_to_csv(output_file)
        print(f"\n✅ Success! Catalog saved to: {output_file}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
