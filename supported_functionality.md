# Supported SPSS Functionality in Legacy ETL Compiler

## Overview
This document outlines the current level of support for SPSS syntax and features in the Legacy ETL Compiler. The compiler parses SPSS scripts, builds an intermediate representation (IR), optimizes the pipeline, and generates equivalent R code using the tidyverse ecosystem.

## Fully Supported Features

### Data Loading
- **GET DATA /TYPE=TXT /FILE='filename.csv' /DELIMITERS=','**
  - Loads CSV files with comma delimiters
  - Supports FIRSTCASE parameter for skipping rows
  - Generates `read_csv()` in R

- **GET DATA /TYPE=SAV /FILE='filename.sav'**
  - Loads SPSS .sav files
  - Generates `read_sav()` in R

### Data Manipulation
- **SORT CASES BY variable(s) (A/D)**
  - Sorts data by one or more variables
  - Supports ascending (A) and descending (D) order
  - Generates `arrange()` in R

- **COMPUTE target = expression**
  - Basic arithmetic and logical expressions
  - Variable assignments
  - Generates `mutate()` in R

- **IF (condition) target = expression**
  - Conditional column assignment
  - Generates `mutate()` with `if_else()` in R

- **RECODE source_vars (...) INTO target_vars**
  - Variable recoding with mapping rules
  - In-place updates when no INTO clause
  - Generates appropriate R transformations

### Data Filtering
- **SELECT IF (condition)**
  - Row filtering based on conditions
  - Generates `filter()` in R

### Data Joining
- **MATCH FILES /FILE=* /TABLE='file' /BY key**
  - Inner and left joins
  - Multiple key variables
  - Generates `inner_join()` and `left_join()` in R

### Aggregation
- **AGGREGATE /BREAK=group_vars /target=func(source)**
  - Grouped aggregations
  - Functions: MEAN, SUM, MAX, MIN
  - Generates `group_by()` and `summarise()` in R

### Schema Definition
- **DATA LIST FREE / var1 (F8.0) var2 (A10)**
  - Variable type definitions
  - Basic format specifications
  - Injected into IR schema

### Data Saving
- **SAVE OUTFILE='filename.sav'**
  - Saves to SPSS .sav format
  - Generates `write_sav()` in R

- **SAVE OUTFILE='filename.csv'**
  - Saves to CSV format
  - Generates `write_csv()` in R

## Supported Functions and Operators

### Mathematical Functions
- TRUNC() → floor()
- RND() → round()
- ABS() → abs()
- MOD(a,b) → a %% b

### String Functions
- CONCAT() → paste0()
- PASTE() → paste0()
- STR_C() → str_c()

### Statistical Functions
- MEAN() → mean()
- LAG() → lag()

### Logical Operators
- AND → &
- OR → |
- <> → !=
- = → == (in expressions)

### Conditional Functions
- IF_ELSE() → if_else()
- CASE_WHEN() → case_when()
- NA_IF() → na_if()

### Date Functions
- DATE.MDY(m,d,y) → make_date(year=y, month=m, day=d)

### Special Values
- $SYSMIS → NA

## Partially Supported Features

### Conditional Logic
- **DO IF / END IF blocks**
  - Basic structure recognized
  - May have formatting inconsistencies in generated conditions

### Generic Commands
- Unknown SPSS commands parsed as generic nodes
- Logged as warnings in generated R code
- No functional implementation

## Unsupported Features

### Data Input
- Complex DATA LIST formats beyond FREE
- BEGIN DATA / END DATA inline data blocks (skipped)
- Other file types beyond TXT and SAV
- Complex delimiter specifications

### Advanced Functions
- Most SPSS-specific functions not in the registry
- Advanced string manipulation beyond CONCAT
- Complex date/time operations beyond MDY
- Missing value patterns beyond $SYSMIS

### Control Flow
- Complex nested IF/DO IF structures
- LOOP/END LOOP constructs
- Macro definitions and calls

### Output
- Complex SAVE options and formats
- EXPORT commands
- PRINT/WRITE statements

### Statistical Procedures
- All statistical analysis commands (DESCRIPTIVES, FREQUENCIES, etc.)
- Parsed as generic nodes with warnings

### File Management
- FILE HANDLE definitions
- Complex file path handling
- Temporary file management

## Test Coverage

### Passing Tests (73/74)
- Data loading and saving
- Basic sorting and filtering
- Simple and conditional computes
- Aggregation operations
- Join operations
- Schema propagation
- Pipeline construction

### Known Issues
- Conditional IF formatting: Extra parentheses in condition expressions
- Some edge cases in expression parsing
- Limited support for complex nested operations

## Recommendations for Extension

1. **Expand Function Registry**: Add more SPSS functions to the transpiler
2. **Improve Expression Parsing**: Handle complex nested expressions and operator precedence
3. **Add Data Type Support**: Support more SPSS data formats and missing value patterns
4. **Implement Control Flow**: Full DO IF/END IF and LOOP support
5. **Enhance File I/O**: Support for additional file formats and options
6. **Add Statistical Procedures**: Implement common analysis commands where applicable

## Current Reliability
The compiler successfully handles basic ETL pipelines with data loading, transformation, filtering, joining, aggregation, and saving. Generated R code uses tidyverse for readability and performance. Complex SPSS scripts with advanced features will generate warnings and may require manual review of the output.