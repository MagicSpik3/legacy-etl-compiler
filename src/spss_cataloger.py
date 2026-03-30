"""
SPSS File Cataloger - Reverse engineering tool for legacy SPSS codebases.

Scans a directory structure for .sps files and extracts:
- File location and name
- Variables used (COMPUTE, SORT CASES, etc.)
- Input files referenced (GET FILE, GET DATA)
- Output files referenced (SAVE OUTFILE, SAVE FILE)

Outputs results to CSV.
"""

import os
import csv
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass, field


@dataclass
class SpssFileMetadata:
    """Metadata extracted from a single SPSS file."""
    location: str  # Full path
    filename: str  # Basename
    input_files: Set[str] = field(default_factory=set)
    output_files: Set[str] = field(default_factory=set)
    variables: Set[str] = field(default_factory=set)
    
    def to_rows(self) -> List[Dict]:
        """Generate CSV rows for this file.
        
        Each row represents one relationship (one variable, input, or output).
        If multiple variables/inputs/outputs exist, multiple rows are created.
        """
        rows = []
        
        # Collect all items
        all_items = []
        for var in sorted(self.variables):
            all_items.append(('variable', var))
        for inp in sorted(self.input_files):
            all_items.append(('input', inp))
        for out in sorted(self.output_files):
            all_items.append(('output', out))
        
        # If no items found, create one row with empty fields
        if not all_items:
            rows.append({
                'location': self.location,
                'filename': self.filename,
                'input_file_referenced': '',
                'output_file_referenced': '',
                'contains_variable': ''
            })
        else:
            # Create one row per item
            for item_type, item_value in all_items:
                row = {
                    'location': self.location,
                    'filename': self.filename,
                    'input_file_referenced': item_value if item_type == 'input' else '',
                    'output_file_referenced': item_value if item_type == 'output' else '',
                    'contains_variable': item_value if item_type == 'variable' else ''
                }
                rows.append(row)
        
        return rows if rows else [{
            'location': self.location,
            'filename': self.filename,
            'input_file_referenced': '',
            'output_file_referenced': '',
            'contains_variable': ''
        }]


class SpssParser:
    """Parses SPSS syntax to extract metadata."""
    
    # Regex patterns for different SPSS statements
    PATTERNS = {
        # GET FILE / GET DATA with file paths
        'get_file': re.compile(
            r'GET\s+FILE\s*=\s*["\']?([^"\';\n]+)["\']?',
            re.IGNORECASE | re.MULTILINE
        ),
        'get_data_file': re.compile(
            r'/FILE\s*=\s*["\']?([^"\';\n]+)["\']',
            re.IGNORECASE | re.MULTILINE
        ),
        # SAVE OUTFILE / SAVE FILE
        'save_outfile': re.compile(
            r'SAVE\s+OUTFILE\s*=\s*["\']?([^"\';\n]+)["\']?',
            re.IGNORECASE | re.MULTILINE
        ),
        'save_file': re.compile(
            r'SAVE\s+FILE\s*=\s*["\']?([^"\';\n]+)["\']?',
            re.IGNORECASE | re.MULTILINE
        ),
        # COMPUTE statements: extract variable names being assigned
        'compute': re.compile(
            r'COMPUTE\s+([A-Za-z_]\w*)\s*=',
            re.IGNORECASE | re.MULTILINE
        ),
        # SORT CASES: extract variable names
        'sort_cases': re.compile(
            r'SORT\s+CASES\s+BY\s+([A-Za-z_]\w*(?:\s+\([AD]\))?(?:\s+[A-Za-z_]\w*(?:\s+\([AD]\))?)*)',
            re.IGNORECASE | re.MULTILINE
        ),
        # Variable declarations: TYPE, STRING, NUMERIC declarations
        'variable_decl': re.compile(
            r'(?:STRING|NUMERIC|FORMAT)\s+([A-Za-z_]\w*)',
            re.IGNORECASE | re.MULTILINE
        ),
        # Variables in GET DATA /VARIABLES section
        'get_data_vars': re.compile(
            r'/VARIABLES?\s*=\s*(.*?)(?=/|\.)',
            re.IGNORECASE | re.MULTILINE | re.DOTALL
        ),
    }
    
    def parse_file(self, filepath: str) -> SpssFileMetadata:
        """Parse a single SPSS file and extract metadata."""
        try:
            # Read file with encoding detection
            content = self._read_spss_file(filepath)
        except Exception as e:
            print(f"  ⚠️  Error reading {filepath}: {e}")
            return SpssFileMetadata(
                location=filepath,
                filename=os.path.basename(filepath)
            )
        
        metadata = SpssFileMetadata(
            location=filepath,
            filename=os.path.basename(filepath)
        )
        
        # Extract input files
        metadata.input_files.update(self._extract_input_files(content))
        
        # Extract output files
        metadata.output_files.update(self._extract_output_files(content))
        
        # Extract variables
        metadata.variables.update(self._extract_variables(content))
        
        return metadata
    
    def _read_spss_file(self, filepath: str) -> str:
        """Read SPSS file, trying different encodings."""
        encodings = ['utf-8', 'windows-1252', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    return f.read()
            except (UnicodeDecodeError, LookupError):
                continue
        
        # Fallback: read with errors='replace'
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    
    def _extract_input_files(self, content: str) -> Set[str]:
        """Extract GET FILE and GET DATA file references."""
        files = set()
        
        # GET FILE = "path"
        for match in self.PATTERNS['get_file'].finditer(content):
            filepath = match.group(1).strip().strip('"\'')
            if filepath:
                files.add(filepath)
        
        # GET DATA /FILE= "path"
        for match in self.PATTERNS['get_data_file'].finditer(content):
            filepath = match.group(1).strip().strip('"\'')
            if filepath:
                files.add(filepath)
        
        return files
    
    def _extract_output_files(self, content: str) -> Set[str]:
        """Extract SAVE OUTFILE and SAVE FILE references."""
        files = set()
        
        # SAVE OUTFILE = "path"
        for match in self.PATTERNS['save_outfile'].finditer(content):
            filepath = match.group(1).strip().strip('"\'')
            if filepath:
                files.add(filepath)
        
        # SAVE FILE = "path"
        for match in self.PATTERNS['save_file'].finditer(content):
            filepath = match.group(1).strip().strip('"\'')
            if filepath:
                files.add(filepath)
        
        return files
    
    def _extract_variables(self, content: str) -> Set[str]:
        """Extract variable names from COMPUTE, SORT, and declarations."""
        variables = set()
        
        # COMPUTE var_name = ...
        for match in self.PATTERNS['compute'].finditer(content):
            var_name = match.group(1).strip()
            if var_name and not var_name.upper() in ('IF', 'THEN', 'ELSE'):
                variables.add(var_name)
        
        # SORT CASES BY var_name, var_name2, ...
        for match in self.PATTERNS['sort_cases'].finditer(content):
            var_list = match.group(1)
            # Parse comma-separated or space-separated vars
            var_names = re.findall(r'([A-Za-z_]\w*)', var_list)
            variables.update(var_names)
        
        # STRING/NUMERIC/FORMAT var_name
        for match in self.PATTERNS['variable_decl'].finditer(content):
            var_name = match.group(1).strip()
            if var_name:
                variables.add(var_name)
        
        # Variables in GET DATA /VARIABLES section
        for match in self.PATTERNS['get_data_vars'].finditer(content):
            var_section = match.group(1)
            var_names = re.findall(r'([A-Za-z_]\w*)\s+[FA]\d+', var_section, re.IGNORECASE)
            variables.update(var_names)
        
        return variables


class SpssDirectoryCataloger:
    """Catalogs all SPSS files in a directory tree."""
    
    def __init__(self):
        self.parser = SpssParser()
        self.metadata_list: List[SpssFileMetadata] = []
    
    def catalog_directory(self, root_dir: str, recursive: bool = True) -> List[SpssFileMetadata]:
        """Scan directory for .sps files and catalog them."""
        pattern = "**/*.sps" if recursive else "*.sps"
        sps_files = list(Path(root_dir).glob(pattern))
        
        print(f"📂 Found {len(sps_files)} SPSS files in {root_dir}")
        
        for filepath in sps_files:
            print(f"  📄 Parsing: {filepath}")
            metadata = self.parser.parse_file(str(filepath))
            self.metadata_list.append(metadata)
            print(f"     → {len(metadata.variables)} variables, "
                  f"{len(metadata.input_files)} inputs, "
                  f"{len(metadata.output_files)} outputs")
        
        return self.metadata_list
    
    def save_to_csv(self, output_path: str):
        """Write catalog to CSV file."""
        rows = []
        for metadata in self.metadata_list:
            rows.extend(metadata.to_rows())
        
        if not rows:
            print("⚠️  No metadata to write.")
            return
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=['location', 'filename', 'input_file_referenced', 
                           'output_file_referenced', 'contains_variable']
            )
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"✅ Catalog saved to: {output_path}")
        print(f"   Total rows: {len(rows)}")
