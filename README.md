# 🚀 Enterprise ETL Compiler Platform

How to run:

# Deactivate any active conda environments
conda deactivate

# Activate the local Python virtual environment
source venv/bin/activate

# (Optional) Verify versioning is recognized
python3 -c "from importlib.metadata import version; print(version('spec_generator'))"

# Navigate to your data/logic folder
cd git/SPSS-examplles/was/

# Run the compiler pointing to the manifest
(venv) jonny@jonny-MS-7B98:~/git/legacy-etl-compiler$ python src/compiler.py --manifest ~/git_etl_old/SPSS-examplles/hello_world/hello.sps
🚀 Starting V&V Compilation Cycle...
📂 Artifacts will be saved to: dist/verification

[Stage 1] Source Verification
  ⚙️  Executed: pspp -> 01_source_verification.txt

[Stage 2] Parsing & Raw Topology
  📝 Saved: 02_raw_topology.yaml

[Stage 3] Optimization
  📝 Saved: 03_optimized_topology.yaml
  📉 Compression: 3 ops -> 3 ops

[Stage 4] Code Generation
  💾 Writing Final R Script to: dist/pipeline.R
  📝 Saved: 04_generated_code.R

[Stage 5] Target Verification (R Execution)
  ⚙️  Executed: Rscript -> 05_target_verification.txt

✅ V&V Cycle Complete.
(venv) jonny@jonny-MS-7B98:~/git/legacy-etl-compiler$ 

# or 
# From the root of the legacy-etl-compiler project:
./etl_compiler.sh demo/input/my_logic.sps demo/input/data.csv

# Run the full test suite with PYTHONPATH defined
PYTHONPATH=src:. pytest -vs

# Run the specific system integration test for PSPP compliance
PYTHONPATH=src:. pytest -vs tests/test_system_integration.py::TestSystemIntegration::test_pspp_compliance[01_load_sort_save]


> **Status:** Production Ready (MVP) | **Version:** 1.0.0

The **Enterprise ETL Compiler** is a modular platform designed to automate the migration of legacy data logic (SPSS) into modern, maintainable data pipelines (R/Tidyverse).

Unlike manual migration, which is error-prone and slow, this compiler builds a mathematical model of the logic, optimizes it for performance and security, and generates strictly typed code automatically.

## 🏗 Architecture

The platform is composed of 4 independent, decoupled libraries:

1.  **`spec_generator` (Frontend):** Parses legacy SPSS into an Abstract Syntax Tree (AST).
2.  **`etl-ir-core` (Protocol):** The shared "Intermediate Representation" (IR) that enforces type safety.
3.  **`etl_optimizer` (Optimizer):** Performs Dead Code Elimination, Logic Collapsing, and Security Audits.
4.  **`etl-r-generator` (Backend):** Generates idiomatic, human-readable Tidyverse code.

## ⚡ Quick Start

**Installation**
```bash
pip install -r requirements.txt

```

**Usage**
To compile a legacy project defined in `compiler.yaml`:

```bash
python3 src/compiler.py --manifest compiler.yaml

```

**Example Output**
The compiler turns spaghetti logic:

```spss
COMPUTE x = 1.
IF (y > 10) z = 2.
EXECUTE.

```

Into clean Tidyverse pipelines:

```r
df <- df %>%
  mutate(x = 1) %>%
  mutate(z = if_else(y > 10, 2, z))

```

## ✅ Key Benefits

* **100% Deterministic:** No "copy-paste" errors.
* **Self-Optimizing:** Automatically removes unused variables (Dead Code Elimination).
* **Audit-Ready:** Detects "Ghost Columns" (variables used before definition) before code is even generated.

```

---

### 2. The Protocol (`etl-ir-core`)
**Location:** `~/git/etl-ir-core/README.md`
**Audience:** Architects & Developers.

```markdown
# 🧠 ETL IR Core (Intermediate Representation)

This library defines the **Strict Type System** for the compiler platform. It serves as the contract between the Parser (SPSS) and the Generator (R).

## Why It Matters
By decoupling the input language from the output language, we avoid an $N \times M$ complexity problem. We parse once to IR, and can generate code for **R**, **Python**, **SQL**, or **Excel** from the same model.

## Data Structures
* **`Pipeline`**: The top-level container carrying Metadata, Datasets, and Operations.
* **`Operation`**: Atomic logic units (e.g., `COMPUTE_COLUMNS`, `FILTER_ROWS`).
* **`DataType`**: Strict enum types ensuring we never mix Strings and Integers accidentally.

## Usage
```python
from etl_ir.model import Pipeline, Operation
# Strictly typed validation via Pydantic

```

```

---

### 3. The Frontend (`spec_generator`)
**Location:** `~/git/spec_generator/README.md`
**Audience:** The "Archaeologist" (You).

```markdown
# 🔍 SPSS Specification Generator

The "Frontend" of the compiler. This library is responsible for ingesting legacy source code (SPSS Syntax) and standardizing it into the compiler's Intermediate Representation (IR).

## Capabilities
* **Lexical Analysis:** Tokenizes raw SPSS syntax.
* **AST Construction:** Builds a tree of `ComputeNode`, `FilterNode`, etc.
* **Graph Builder:** Converts the AST into a directed acyclic graph (DAG) of data flow.

## supported Commands
* `DATA LIST` / `GET DATA`
* `COMPUTE` / `IF`
* `SELECT IF` / `FILTER`
* `MATCH FILES` (Joins)
* `AGGREGATE`

```

---

### 4. The Brain (`etl_optimizer`)

**Location:** `~/git/etl_optimizer/README.md`
**Audience:** Data Engineers & Security.

```markdown
# ⚡ ETL Semantic Optimizer

The "Brain" of the compiler. This engine takes the raw logic graph and improves it using compiler optimization techniques.

## Optimization Passes
1.  **Semantic Promotion:** Promotes generic text commands into typed Semantic Nodes.
2.  **Vertical Collapsing:** Merges consecutive row-level operations (`mutate` chains) into single batch operations for performance.
3.  **Dead Code Elimination (DCE):** Identifies and removes variables/datasets that are computed but never saved or used.

## 🛡 Security Validator
The optimizer includes a static analysis tool that detects:
* **Ghost Columns:** Variables referenced before they are defined.
* **Topology Cycles:** Infinite loops in data logic.
* **Disconnected Islands:** Orphaned logic branches.

```

---

### 5. The Backend (`etl-r-generator`)

**Location:** `~/git/etl-r-generator/README.md`
**Audience:** The R Developers / Analysts.

```markdown
# 📉 ETL R-Generator

The "Backend" of the compiler. It translates the Optimized IR Pipeline into production-grade R scripts.

## Design Philosophy
We do not generate "machine code." We generate **Human-Readable** code. The output is designed to look like it was written by a Senior Data Scientist using the `tidyverse`.

## Features
* **Dialect:** Tidyverse (`dplyr`, `readr`, `lubridate`).
* **Visitor Pattern:** Extensible architecture to support new R libraries easily.
* **Formatting:** Auto-indented, commented, and modular code blocks.

```

---
No more guessing—the "Territory" is clear now. According to your `dir()` output, the primary entry point is indeed **`parse`**, but the rest of the class is composed of specialized private methods (like `_parse_get_data` and `_parse_sort`) that handle the heavy lifting.

Since `parse_string` doesn't exist, we should definitely refactor the `SpssParser` class. Currently, your `parse` method likely opens a file path. By splitting it, we allow the unit tests to pass in strings directly, bypassing the filesystem.

### The Refactor: Splitting the "Map" from the "Source"

In your `spec_generator/src/spec_generator/importers/spss/parser.py`, you should restructure your `parse` logic like this:

```python
class SpssParser:
    # ... your __init__ and other methods ...

    def parse(self, file_path):
        """The original entry point for the CLI."""
        with open(file_path, 'r') as f:
            content = f.read()
        return self.parse_string(content)

    def parse_string(self, text):
        """The new entry point for Unit Tests."""
        # 1. Tokenize the text
        # 2. Loop through tokens and call your _parse_ methods
        # 3. Return the topology (list of IR operations)
        
        # This is where your existing logic from the old 'parse' 
        # should now live.
        self.tokens = self.tokenize(text) # Assuming you have a tokenizer
        self.pos = 0
        return self._do_parse_logic() 

```

---

### Updated Unit Test

Once you’ve added `parse_string` to the class, your unit test will work exactly as we wrote it:

```python
def test_load_parameter_integrity():
    spss_content = """
    GET DATA
      /TYPE=TXT
      /FILE='test.csv'
      /FIRSTCASE=2
      /VARIABLES=id F8.0.
    """
    parser = SpssParser()
    # This now works because we've added the method to the class!
    topology = parser.parse_string(spss_content)
    
    load_op = next(op for op in topology if op.type == "LOAD_CSV")
    assert load_op.params['skip_rows'] == 1

```

### Why this is the "Engineer's Choice"

* **Test Speed:** Disk I/O is slow. Testing strings in memory is near-instant.
* **Flexibility:** If you ever decide to build a web-based "SPSS to R" converter, you can pass the text from a web form straight into `parse_string` without saving it to a temporary file first.
* **Clarity:** It separates the **Transport Layer** (getting the file from the disk) from the **Logic Layer** (understanding what the SPSS actually says).

### A Note on the `_parse_` methods

I see `_parse_get_data`, `_parse_sort`, and `_parse_variables_block` in your `dir()` output. These are the internal gears. If your `parse_string` refactor goes well, your unit tests are effectively exercising these private gears in a controlled environment.

**Would you like me to help you draft the `parse_string` implementation based on how your `advance()` and `peek_token()` methods currently work?**