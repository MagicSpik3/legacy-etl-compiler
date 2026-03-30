# SPSS Cataloger - Advanced Customization

If you need to extract additional patterns or modify the behavior of the cataloger, here's how to extend it.

## Adding Custom Variable Extraction Patterns

The `SpssParser` class uses regex patterns to extract information. To add support for additional SPSS statements:

### Example: Extract variables from SELECT IF statements

```python
from spss_cataloger import SpssParser

# Create a custom parser by extending the class
class CustomSpssParser(SpssParser):
    def __init__(self):
        super().__init__()
        # Add or override patterns
        self.PATTERNS['select_if'] = re.compile(
            r'SELECT\s+IF\s*\(\s*([A-Za-z_]\w*)',
            re.IGNORECASE | re.MULTILINE
        )
    
    def _extract_variables(self, content: str):
        variables = super()._extract_variables(content)
        
        # Extract from SELECT IF
        for match in self.PATTERNS['select_if'].finditer(content):
            var_name = match.group(1).strip()
            if var_name:
                variables.add(var_name)
        
        return variables
```

### Example: Extract file paths from INSERT FILE statements

```python
class CustomSpssParser(SpssParser):
    def __init__(self):
        super().__init__()
        self.PATTERNS['insert_file'] = re.compile(
            r'INSERT\s+FILE\s*=\s*["\']?([^"\';\n]+)["\']?',
            re.IGNORECASE | re.MULTILINE
        )
    
    def _extract_input_files(self, content: str):
        files = super()._extract_input_files(content)
        
        # Extract from INSERT FILE
        for match in self.PATTERNS['insert_file'].finditer(content):
            filepath = match.group(1).strip().strip('"\'')
            if filepath:
                files.add(filepath)
        
        return files
```

## Creating a Filtered Cataloger

If you only want to catalog files that meet certain criteria:

```python
from spss_cataloger import SpssDirectoryCataloger, SpssFileMetadata

class FilteredCataloger(SpssDirectoryCataloger):
    def __init__(self, filter_func=None):
        super().__init__()
        self.filter_func = filter_func or (lambda m: True)
    
    def catalog_directory(self, root_dir, recursive=True):
        # Call parent to do the scanning
        super().catalog_directory(root_dir, recursive)
        
        # Filter results
        self.metadata_list = [
            m for m in self.metadata_list
            if self.filter_func(m)
        ]
        
        print(f"  🔍 Filtered to {len(self.metadata_list)} files")
        return self.metadata_list

# Usage: Only catalog files with "DV" in the name
cataloger = FilteredCataloger(
    filter_func=lambda m: 'DV' in m.filename
)
cataloger.catalog_directory('/path/to/files')
cataloger.save_to_csv('dv_only_catalog.csv')
```

## Post-Processing Results

After generating the CSV, you can post-process it for analysis:

```python
import pandas as pd

# Load the catalog
df = pd.read_csv('spss_catalog.csv')

# Find all files that reference a specific input
income_files = df[df['input_file_referenced'].str.contains('income', na=False)]
print(income_files[['location', 'filename']])

# Find all unique variables across all files
all_variables = df[df['contains_variable'].notna()]['contains_variable'].unique()
print(f"Total unique variables: {len(all_variables)}")

# Find files with most dependencies
file_deps = df.groupby('filename').size().sort_values(ascending=False)
print(file_deps.head(10))
```

## Handling Complex SPSS Syntax

### Macros and Conditional Logic

The current parser does not expand SPSS macros. If you have files with heavy macro usage, you may want to pre-process them:

```python
def preprocess_spss_content(content):
    """Remove or expand common SPSS macros."""
    # Example: Remove commented macro definitions
    content = re.sub(r'^\s*\*.*MACRO.*$', '', content, flags=re.MULTILINE)
    return content

# Use in custom parser:
class MacroAwareParser(SpssParser):
    def _read_spss_file(self, filepath):
        content = super()._read_spss_file(filepath)
        return preprocess_spss_content(content)
```

### DO IF ... END IF Blocks

Variables inside DO IF blocks are still captured, which is correct for dependency analysis. If you need to distinguish them:

```python
self.PATTERNS['do_if_block'] = re.compile(
    r'DO\s+IF\s*\((.*?)\)\s*\.\s*(.*?)\s*END\s+IF',
    re.IGNORECASE | re.MULTILINE | re.DOTALL
)

# Extract variables only from the conditional block
for match in self.PATTERNS['do_if_block'].finditer(content):
    condition = match.group(1)
    block = match.group(2)
    # Variables here can be tagged as "conditional"
```

## Performance Optimization

For very large codebases (10,000+ files):

```python
from concurrent.futures import ThreadPoolExecutor
from spss_cataloger import SpssParser
from pathlib import Path

class ParallelCataloger:
    def __init__(self, num_workers=4):
        self.parser = SpssParser()
        self.num_workers = num_workers
        self.metadata_list = []
    
    def catalog_directory(self, root_dir, recursive=True):
        pattern = "**/*.sps" if recursive else "*.sps"
        sps_files = list(Path(root_dir).glob(pattern))
        
        print(f"📂 Found {len(sps_files)} files. Processing with {self.num_workers} workers...")
        
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            results = executor.map(self.parser.parse_file, [str(f) for f in sps_files])
            self.metadata_list = list(results)
        
        return self.metadata_list
    
    def save_to_csv(self, output_path):
        # Same as base class
        pass
```

## Integration with Your Compiler

The cataloger integrates with your existing ETL compiler pipeline. To add it as a default task:

1. Update your `compiler.yaml` manifests to include cataloging:

```yaml
inputs:
  spss_directory: /path/to/spss/files
  primary_logic: logic.sps

catalog:
  enabled: true
  output: dist/spss_catalog.csv
```

2. Update `compile_pipeline()` to check for catalog config and run it automatically.

## Debugging and Validation

### Inspect what's being extracted from a single file

```python
from spss_cataloger import SpssParser

parser = SpssParser()
metadata = parser.parse_file("/path/to/test_file.sps")

print(f"File: {metadata.filename}")
print(f"Variables: {sorted(metadata.variables)}")
print(f"Input files: {sorted(metadata.input_files)}")
print(f"Output files: {sorted(metadata.output_files)}")
```

### Validate regex patterns before use

```python
import re

test_line = 'COMPUTE MYLft1R8 = ...'
pattern = re.compile(r'COMPUTE\s+([A-Za-z_]\w*)\s*=', re.IGNORECASE)
match = pattern.search(test_line)
if match:
    print(f"Matched: {match.group(1)}")  # Output: MYLft1R8
```

## Common Pitfalls

1. **Whitespace sensitivity**: SPSS syntax is flexible with whitespace. Ensure regex patterns allow for multiple spaces/tabs: `\s+` not single space.

2. **Quoted paths**: File paths may be quoted with single or double quotes: `"path"` or `'path'` or unquoted: `path`.

3. **Comments**: Comments in SPSS start with `*`. Be careful not to extract variable names from comments.

4. **Case sensitivity**: SPSS is case-insensitive for keywords but case-sensitive for variable names. Regex patterns use `re.IGNORECASE` for keywords.

5. **Encoding issues**: Always read files with fallback encoding support.

## Testing Your Customizations

Create a test file with edge cases and validate:

```python
def test_custom_patterns():
    parser = CustomSpssParser()
    
    test_cases = [
        ("COMPUTE  var1  = 5", ['var1']),
        ("COMPUTE\tvar2\t=\t10", ['var2']),
        ("* COMPUTE comment_var = ...", []),  # Should skip comments
        ("SELECT IF (var3 > 0).", ['var3']),
    ]
    
    for spss_code, expected_vars in test_cases:
        result = parser._extract_variables(spss_code)
        assert result == set(expected_vars), f"Failed: {spss_code}"
    
    print("✅ All tests passed!")

test_custom_patterns()
```

