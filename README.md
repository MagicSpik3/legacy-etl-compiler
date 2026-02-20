# Legacy ETL Compiler — README

Summary
-------
This repository is the legacy ETL compiler orchestration and entry point for a multi-repo ETL compiler platform. The project ingests legacy SPSS/PSPP logic, converts it into a structured intermediate representation (IR), applies semantic optimization and validation passes, and finally generates idiomatic R (tidyverse) code. The compiler performs static checks (e.g. ghost-column detection) and produces verification artifacts at each stage so changes are auditable.

This README explains: intent, architecture, the compilation "State Machine", how to run the compiler on Linux and Windows, example invocations and expected artifact outputs, and short developer notes for common tasks.

Intent & Use Cases
------------------
- Migrate legacy SPSS/PSPP analysis logic into reproducible, maintainable pipelines (R/Tidyverse).
- Provide deterministic transformations so audit and compliance teams can review identical semantics between legacy and generated code.
- Offer a modular pipeline so different frontends (parsers) or backends (code generators) can be swapped independently.

Repository Roles (high-level)
----------------------------
- `legacy-etl-compiler` (this repo): CLI & orchestration that wires together the other repos and exposes a manifest-based entrypoint.
- `spec_generator`: SPSS/PSPP parser & AST → Graph builder.
- `etl-ir-core`: Pydantic-based Intermediate Representation (IR) models shared across components.
- `etl_optimizer`: Optimization and validation passes (semantic promotion, dead-code elimination, validators).
- `etl-r-generator`: Generates R/Tidyverse code from the optimized IR.

Compilation State Machine (overview)
-----------------------------------
The compiler executes a small state machine with deterministic stages. Each stage produces artifacts preserved under `dist/verification` to enable traceability.

States & transitions
- START: CLI starts, manifest parsed, locations resolved.
- SOURCE_VERIFICATION: (State) runs tools like `pspp` to verify/convert input data sources. Produces `01_source_verification.txt`.
- PARSING: (State) `spec_generator` parses SPSS text into an AST and initial topology. Produces `02_raw_topology.yaml`.
- OPTIMIZATION: (State) `etl_optimizer` executes passes:
  - Semantic Promotion (promote GENERIC ops into semantic ops like COMPUTE_COLUMNS).
  - Vertical Collapsing (merge row-level mutates into batches).
  - Validator (ghost column detection, topology cycles, disconnected islands).
  Produces `03_optimized_topology.yaml` and stops with an error if validation fails.
- CODE_GENERATION: (State) `etl-r-generator` translates the optimized IR into an R script. Produces `04_generated_code.R` (and optionally `dist/pipeline.R`).
- TARGET_VERIFICATION: (Optional State) runs the generated R script to validate successful execution (produces `05_target_verification.txt`).
- DONE: Completed successfully or errored with artifact outputs and logs.

Error handling
- If the Validator stage finds a critical issue (e.g. ghost column), the run ends early and the diagnostics are saved in `dist/verification`.

Artifacts (typical)
- `dist/verification/01_source_verification.txt` — Source tool output (pspp or other checks).
- `dist/verification/02_raw_topology.yaml` — Parser output (raw operations and datasets).
- `dist/verification/03_optimized_topology.yaml` — Optimizer output (promoted operations).
- `dist/verification/04_generated_code.R` — Generated R script (readable by humans).
- `dist/verification/05_target_verification.txt` — Output of test-run of the generated R code (optional).

Quick Requirements
------------------
- Python 3.10+ (3.11/3.12 tested).
- `pip` for installing Python dependencies (or use `conda`).
- On systems that need SPSS parsing emulation, `pspp` may be required for some tests.

Environment Setup — Linux (bash)
--------------------------------
1. Create & activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

2. If working across the sibling repos (common for development), use a PYTHONPATH that points each `src` directory at the workspace root. Example using absolute paths (from your workspace root):

```bash
export BASE=/home/you/git
export PYTHONPATH="$BASE/legacy-etl-compiler/src:$BASE/spec_generator/src:$BASE/etl-ir-core/src:$BASE/etl_optimizer/src:$BASE/etl-r-generator/src:"
```

Environment Setup — Windows (PowerShell)
---------------------------------------
1. Create & activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

2. Set PYTHONPATH for local development (PowerShell example):

```powershell
$Base = 'C:\Users\you\git'
$env:PYTHONPATH = "$Base\legacy-etl-compiler\src;$Base\spec_generator\src;$Base\etl-ir-core\src;$Base\etl_optimizer\src;$Base\etl-r-generator\src"
```

Running the Compiler (manifest-driven)
--------------------------------------
1. Prepare a simple manifest file `compiler.yaml` (example):

```yaml
project: "My Migration"
inputs:
  primary_logic: path/to/logic.sps
  # option: primary_data: path/to/data.csv
output:
  target: r_script
  path: dist/pipeline.R
```

2. Run the CLI (Linux/Windows as appropriate):

```bash
# From the repo root; ensure PYTHONPATH includes sibling src directories when developing
python src/compiler.py --manifest compiler.yaml
```

Expected output (short):

- `dist/verification/01_source_verification.txt` — source check output
- `dist/verification/02_raw_topology.yaml` — raw parser topology
- `dist/verification/03_optimized_topology.yaml` — optimizer output
- `dist/verification/04_generated_code.R` — final R code

Developer notes & debugging tips
--------------------------------
- Running tests: always run with the multi-repo PYTHONPATH. Example (Linux):

```bash
PYTHONPATH=$PWD/src:$PWD/../spec_generator/src:$PWD/../etl-ir-core/src:$PWD/../etl_optimizer/src:$PWD/../etl-r-generator/src pytest -q
```

- If you see "Ghost Column" validation failures (e.g. a validator error referencing `'lag'`):
  1. Inspect `dist/verification/02_raw_topology.yaml` to see how the parser emitted the compute expression.
  2. Confirm the parser recognized `LAG()` and treated it as a function rather than a column name.
  3. Confirm `etl_optimizer` `KNOWN_FUNCTIONS` includes `LAG` and `CONCAT` (or add them) so the validator ignores them as variables.

- To run a single integration test (example) with correct environment:

```bash
PYTHONPATH=$PWD/src:$PWD/../spec_generator/src:$PWD/../etl-ir-core/src:$PWD/../etl_optimizer/src:$PWD/../etl-r-generator/src pytest -q tests/test_system_integration.py::TestSystemIntegration::test_pspp_compliance[05_lag]
```

Common Development tasks
------------------------
- Add a `parse_string()` method to the SPSS parser (in `spec_generator`) so unit tests can feed SPSS text without file I/O.
- When modifying the promoter in `etl_optimizer` add unit tests that assert promoted op kinds for `MISSING`, `RECODE`, and `DO IF`.
- When tweaking codegen, run the optimizer integration tests to ensure code style/keywords expected by tests (e.g. `paste0` vs `str_c`, `left_join` vs `inner_join`).

Example: small end-to-end scenario
---------------------------------
Given a simple SPSS logic file `logic.sps`:

```spss
GET DATA /TYPE=TXT /FILE='data.csv' /FIRSTCASE=2.
SORT CASES BY id.
COMPUTE prev = LAG(val).
SAVE OUTFILE='out.sav'.
```

Running the compiler should yield (artifacts):

- `02_raw_topology.yaml`: shows a `LOAD`/`SORT`/`COMPUTE` sequence where `COMPUTE` contains an expression using `lag(val)`.
- `03_optimized_topology.yaml`: `COMPUTE` remains, and validator ignores `lag` if it is recognized as a function.
- `04_generated_code.R`: contains tidyverse-style reads and a `mutate(prev = dplyr::lag(val))` or equivalent mapping depending on generator options.

Notes on the State Machine implementation
----------------------------------------
- The State Machine is simple and deterministic — each state is implemented as a stage function in `src/compiler.py` that receives the current `Pipeline` IR and returns either the next state or an error.
- Each stage appends human-readable artifacts to `dist/verification` which are used by the next stage for debugging and auditing.
- The validator stage is intentionally strict: failures block code generation and require developer action. This is by design to avoid producing code that would silently change semantics.

Where to find important code
----------------------------
- CLI / orchestrator: `src/compiler.py` (entrypoint)
- SPSS parser & AST builder: `../spec_generator/src/spec_generator/importers/spss/` (look for `parser.py` & `graph_builder.py`)
- IR model: `../etl-ir-core/src/etl_ir/` (Pydantic models)
- Optimizer / promoter: `../etl_optimizer/src/etl_optimizer/promoter.py` and `validator.py`
- R generator: `../etl-r-generator/src/etl_r_generator/` (transpiler & builder modules)

Contributing & tests
--------------------
- Add unit tests in each repo under `tests/unit` and integration tests under `tests/integration`.
- Always run `pytest` with the multi-repo `PYTHONPATH` set to ensure modules are resolved correctly during development.

Contact / Support
-----------------
If you need help understanding a specific failing scenario, open an issue or reach out to the team lead with the `dist/verification` artifacts for the failing run attached.

License
-------
See the project `LICENSE` file for details.

— End of README
