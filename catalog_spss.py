#!/usr/bin/env python3
"""
Standalone SPSS Cataloger Script

Usage:
    python catalog_spss.py /path/to/spss/files [output_file.csv]

Example:
    python catalog_spss.py /mnt/nsdata1/MainstageR8 catalog_output.csv
    python catalog_spss.py "/nsdata1/Monthly Processing/2012/5. Checks & Edits/3. Base Checks" catalog_output.csv
    
    

    Z:\MainstageR8\Monthly Processing\2012\5. Checks & Edits\3. Base Checks
"""

import argparse
import os
import sys

# Add src directory to path to import cataloger
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from spss_cataloger import SpssDirectoryCataloger


def main():
    parser = argparse.ArgumentParser(description='Catalog SPSS scripts and extract variable metadata.')
    parser.add_argument('path', help='SPSS .sps file or directory containing .sps files')
    parser.add_argument('output_file', nargs='?', default='spss_catalog.csv', help='CSV output path')
    parser.add_argument('--include-is-new', action='store_true', help='Add an Is New column for variables created by SPSS')
    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"❌ Error: Path not found: {args.path}")
        sys.exit(1)

    print(f"🔍 Scanning: {args.path}")
    print(f"📝 Output will be saved to: {args.output_file}\n")
    
    try:
        cataloger = SpssDirectoryCataloger()
        cataloger.catalog_path(args.path, recursive=True)
        cataloger.save_to_csv(args.output_file, include_is_new=args.include_is_new)
        print(f"\n✅ Success! Catalog saved to: {args.output_file}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
