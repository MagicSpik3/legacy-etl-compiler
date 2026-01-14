#!/bin/bash

# Stops on first error
set -e

# Usage Check
if [ "$#" -ne 2 ]; then
    echo "Usage: ./etl_compiler.sh <path_to_sps> <path_to_csv>"
    echo "Example: ./etl_compiler.sh my_logic.sps my_data.csv"
    exit 1
fi

INPUT_SPS=$(realpath "$1")
INPUT_CSV=$(realpath "$2")
BASENAME=$(basename "$INPUT_SPS" .sps)

# Paths to Repos (Updated for new structure)
REPO_1="components/spec_generator"
REPO_2="components/etl_optimizer"
REPO_3="components/etl-r-generator"
OUTPUT_DIR="output_$BASENAME"


# Clean Setup
echo "🚀 ETL COMPILER: Turning Legacy into Modern"
echo "==========================================="
echo "📂 Input Logic: $INPUT_SPS"
echo "📊 Input Data:  $INPUT_CSV"
echo "📁 Workspace:   $OUTPUT_DIR"
echo "-------------------------------------------"

mkdir -p "$OUTPUT_DIR"
cp "$INPUT_CSV" "$OUTPUT_DIR/$(basename "$INPUT_CSV")"

# 1. PARSE (SpecGen)
echo "📝 [1/4] Parsing Legacy Syntax..."
cd $REPO_1
# Run SpecGen, targeting the input file
PYTHONPATH=src:. python cli.py "$INPUT_SPS" > /dev/null 2>&1
# Move the resulting YAML to our output dir
mv "${INPUT_SPS%.sps}.yaml" "../$OUTPUT_DIR/raw.yaml"
cd ..
echo "   ✅ Syntax Tree Extracted"

# 2. OPTIMIZE (Optimizer)
echo "🧠 [2/4] Optimizing Logic Graph..."
cd $REPO_2
PYTHONPATH=src:. python cli.py "../$OUTPUT_DIR/raw.yaml" \
    --dump-yaml "../$OUTPUT_DIR/optimized.yaml" \
    --visualize "../$OUTPUT_DIR/flow.md" > /dev/null
cd ..
echo "   ✅ Logic Collapsed & Healed"

# 3. GENERATE (R Generator)
echo "⚙️  [3/4] Generating Tidyverse Code..."
cd $REPO_3
PYTHONPATH=src:. python cli.py "../$OUTPUT_DIR/optimized.yaml" \
    --output "../$OUTPUT_DIR/pipeline.R" > /dev/null
cd ..
echo "   ✅ R Script Created: $OUTPUT_DIR/pipeline.R"


# 4. EXECUTE (R Runtime)
echo "🏃 [4/4] Executing R Pipeline..."
cd "$OUTPUT_DIR"

if command -v Rscript &> /dev/null; then
    # Run the pipeline
    Rscript pipeline.R
    echo "   ✅ Execution Complete."

    echo ""
    echo "👀 RESULTS PREVIEW:"
    echo "-------------------"

    # Find any CSV that is NOT the source input file and print it
    # We use 'head' to avoid flooding the screen if the file is huge
    for f in *.csv; do
        if [[ "$f" != "source_$(basename "$INPUT_CSV")" && "$f" != "$(basename "$INPUT_CSV")" ]]; then
            echo "📄 File: $f"
            # 'column -t -s,' aligns the CSV commas into pretty columns
            head -n 10 "$f" | column -t -s, 2>/dev/null || cat "$f"
            echo "..."
        fi
    done
else
    echo "   ⚠️  Skipping execution (R not installed)."
fi
cd ..

echo "==========================================="
echo "🎉 DEMO COMPLETE. Full results in: $OUTPUT_DIR/"
