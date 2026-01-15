# 🚀 Enterprise ETL Compiler Platform

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
