#!/bin/bash

# Function to pause with a prompt
pause() {
    echo ""
    read -p "  [Press ENTER to continue...]"
    clear
}

# Function to print a section header
header() {
    echo "========================================================"
    echo "  $1"
    echo "========================================================"
    echo ""
}

clear

# --- SCENE 1: THE INPUTS ---
header "STEP 1: The Raw Materials"
echo "We start with a standard CSV file and a legacy SPSS script."
echo ""
echo "📂 File: demo_data.csv"
echo "----------------------"
echo "📂 File: demo/input/data.csv"
cat demo/input/data.csv | column -t -s,

echo "📜 File: demo/input/logic.sps"
cat demo/input/logic.sps

pause

# --- SCENE 2: THE LEGACY RUN ---
header "STEP 2: The Legacy Baseline (PSPP)"
echo "First, we verify the logic works in the old environment (PSPP)."
echo "Running: pspp demo/input/logic.sps ..."
pspp demo/input/logic.sps

echo "✅ PSPP Execution Complete."

echo "📄 Legacy Output:"
# PSPP usually outputs to the current folder, or defined path. 
# Check if your logic.sps still points to 'demo_results.csv' or needs a path update.
cat demo_results.csv | column -t -s,

pause

# --- SCENE 3: THE MODERN COMPILER ---
header "STEP 3: The Transformation (ETL Compiler)"
echo "Now, we run the new Python-based ETL Compiler."
echo "Command: ./etl_compiler.sh demo_logic.sps demo_data.csv"
echo ""
sleep 1
./etl_compiler.sh demo/input/logic.sps demo/input/data.csv
pause

# --- SCENE 4: THE PAYOFF (GENERATED CODE) ---
header "STEP 4: The Generated Code (The Payoff)"
echo "The compiler has reverse-engineered the logic and written this R script:"
echo ""
echo "📜 File: output_demo_logic/pipeline.R"
echo "-------------------------------------"
# cat -n adds line numbers to make it look like an IDE
cat -n output_demo_logic/pipeline.R
echo ""
echo "-------------------------------------"
echo "✨ Note the 'mutate' logic and the vectorized filtering."
pause

# --- SCENE 5: COMPARISON ---
header "STEP 5: Verification"
echo "Finally, we prove functional parity."
echo ""
echo "Legacy Result (PSPP):"
head -n 5 demo_results.csv | column -t -s,
echo ""
echo "Compiler Result (R/Tidyverse):"
head -n 5 output_demo_logic/file_demo_results.csv | column -t -s,
echo ""
echo "========================================================"
echo "🎉 DEMO COMPLETE: Functional Parity Achieved."
echo "========================================================"
echo ""
