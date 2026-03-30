# SPSS File Cataloger - Usage Guide

A reverse engineering tool integrated into your ETL compiler that catalogs legacy SPSS file structures.

## Features

- **Recursive scanning** of `.sps` files in nested directory structures
- **Variable extraction** from COMPUTE, SORT CASES, FORMAT, NUMERIC, STRING declarations
- **File reference extraction** from GET FILE, GET DATA, SAVE OUTFILE, SAVE FILE statements
- **Multiple encoding support** (UTF-8, Windows-1252, Latin-1)
- **CSV output** for analysis in Excel, pandas, or other tools

## Installation

Your cataloger is already installed as part of the compiler. No additional dependencies required beyond what's in `requirements.txt`.

## Usage

### Basic Command

```bash
python src/compiler.py catalog --directory /path/to/spss/files --output catalog.csv
```

### Options

- `--directory PATH` (required): Root directory containing your SPSS files
- `--output FILENAME` (default: `spss_catalog.csv`): Output CSV filename
- `--recursive` (default: True): Recursively scan subdirectories (use `--no-recursive` to disable)

### Examples

#### 1. Catalog all SPSS files from a network mount

```bash
python src/compiler.py catalog --directory /mnt/nsdata1/MainstageR8 --output spss_full_catalog.csv
```

#### 2. Catalog only top-level SPSS files (no subdirectories)

```bash
python src/compiler.py catalog --directory /mnt/nsdata1/MainstageR8 --no-recursive
```

#### 3. Catalog to a specific output location

```bash
python src/compiler.py catalog \
    --directory /mnt/nsdata1/MainstageR8 \
    --output /home/jonny/analysis/catalog.csv
```

## Output Format

The CSV contains the following columns:

| Column                      | Description |
|-----------------------------|-------------|
| `location`                  | Full file path (e.g., `/mnt/nsdata1/MainstageR8/Imputation/3. DV Creation/1. DV Housing.sps`) |
| `filename`                  | Basename of the file (e.g., `1. DV Housing.sps`) |
| `input_file_referenced`     | File referenced by GET FILE or GET DATA (blank if none) |
| `output_file_referenced`    | File written by SAVE OUTFILE or SAVE FILE (blank if none) |
| `contains_variable`         | Variable name extracted from the file (blank if none) |

### Output Structure

Each row represents **one relationship** (one variable, input, or output):

- If a file has 5 variables, 2 input files, and 1 output file, it generates **8 rows** (one per item)
- Files with no variables/inputs/outputs generate 1 row with empty fields
- This allows easy filtering and analysis in spreadsheet tools

### Example Output

```csv
location,filename,input_file_referenced,output_file_referenced,contains_variable
/path/to/Prev_Waves_Corrections.sps,Prev_Waves_Corrections.sps,r7_minimal.csv,,
/path/to/Prev_Waves_Corrections.sps,Prev_Waves_Corrections.sps,,R7_Full_Wave_Linkage_R8 Miss.sav,
/path/to/Prev_Waves_Corrections.sps,Prev_Waves_Corrections.sps,,,DteofbthR7
/path/to/Prev_Waves_Corrections.sps,Prev_Waves_Corrections.sps,,,DVAgeR7
/path/to/Prev_Waves_Corrections.sps,Prev_Waves_Corrections.sps,,,PIDNO
/path/to/Prev_Waves_Corrections.sps,Prev_Waves_Corrections.sps,,,survyear
/path/to/Prev_Waves_Corrections.sps,Prev_Waves_Corrections.sps,,,survmonth
```

## Supported SPSS Statements

The cataloger extracts information from:

### Variables
- **COMPUTE** statements: `COMPUTE var_name = ...`
- **SORT CASES** statements: `SORT CASES BY var1, var2`
- **Variable declarations**: `STRING|NUMERIC|FORMAT var_name`
- **GET DATA /VARIABLES** section: Variable type declarations

### Input Files
- **GET FILE**: `GET FILE = "filename.sav"`
- **GET DATA /FILE**: `GET DATA /TYPE=TXT /FILE="filename.csv"`

### Output Files
- **SAVE OUTFILE**: `SAVE OUTFILE="filename.sav"`
- **SAVE FILE**: `SAVE FILE = "filename.sav"`

## Analysis Workflows

### Find all files that generate a specific output

```bash
grep "output_column_name" catalog.csv
```

### Find all files that use a specific variable

```bash
grep "target_variable" catalog.csv
```

### Build a dependency graph

```bash
# Pivot the CSV to understand data flow:
# Input files → Processing files → Output files
```

### Identify missing files

```bash
# Find referenced files that may not exist or are on another path
grep "input_file_referenced" catalog.csv | grep -v "^," 
```

## Encoding Handling

The tool automatically detects file encodings. If a `.sps` file uses Windows-1252 encoding (common in legacy SPSS), it will be handled correctly. Fallback encoding is UTF-8 with character substitution.

## Performance

- **100 files**: ~1-2 seconds
- **1,000 files**: ~10-20 seconds
- **10,000 files**: ~100-200 seconds

Performance depends on file sizes and average nesting depth.

## Troubleshooting

### "Directory not found"
Ensure the path is correct and you have read access to the network location.

### Missing variables in output
The cataloger uses pattern matching for SPSS syntax. Complex variable declarations or non-standard syntax may not be captured. Check raw `.sps` files manually.

### Encoding issues
If variable names appear garbled, the encoding detection may have failed. Try opening the file in a text editor to confirm encoding, then contact support.

## Integration with Your Compiler

The cataloger is integrated as a new command in your existing CLI:

```bash
python src/compiler.py --help
```

This shows both the existing `build` command and the new `catalog` command.

## Next Steps

1. Run the cataloger on your SPSS directory
2. Open the CSV in Excel or pandas for analysis
3. Use the output to:
   - Map data dependencies
   - Identify orphaned files
   - Plan refactoring efforts
   - Generate documentation
