import click  # <--- NEW: Switch from argparse to click
import os
import subprocess
import shutil
import yaml
from typing import List

# Import your modules
from spec_generator.importers.spss.parser import SpssParser
from spec_generator.importers.spss.graph_builder import GraphBuilder
from etl_optimizer.coordinator import OptimizationCoordinator
from etl_r_generator.builder import RGenerator
from etl_ir.model import Pipeline

class ArtifactManager:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.verification_dir = os.path.join(output_dir, "verification")
        
        # Clean slate
        if os.path.exists(self.verification_dir):
            shutil.rmtree(self.verification_dir)
        os.makedirs(self.verification_dir)
        print(f"📂 Artifacts will be saved to: {self.verification_dir}")

    def save_text(self, filename: str, content: str):
        path = os.path.join(self.verification_dir, filename)
        with open(path, "w") as f:
            f.write(content)
        print(f"  📝 Saved: {filename}")

    def save_topology(self, filename: str, pipeline: Pipeline):
        """Dumps the State Machine (Topology) to a readable YAML-like format."""
        lines = []
        lines.append(f"# Pipeline Topology: {len(pipeline.operations)} Operations")
        lines.append("-" * 40)
        
        for op in pipeline.operations:
            lines.append(f"Operation: {op.id}")
            lines.append(f"  Type:    {op.type.name}")
            lines.append(f"  Inputs:  {op.inputs}")
            lines.append(f"  Outputs: {op.outputs}")
            if op.parameters:
                lines.append(f"  Params:  {op.parameters}")
            lines.append("")
            
        self.save_text(filename, "\n".join(lines))

def run_command(cmd: List[str], log_file: str):
    """Runs a shell command and captures output to a file."""
    try:
        result = subprocess.run(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True
        )
        status = "✅ Success" if result.returncode == 0 else "❌ Failed"
        output = f"Command: {' '.join(cmd)}\nStatus: {status}\n\n=== OUTPUT ===\n{result.stdout}"
    except FileNotFoundError:
        output = f"Command: {' '.join(cmd)}\nStatus: ⚠️ Tool Not Found (Skipped)"
    
    with open(log_file, "w") as f:
        f.write(output)
    print(f"  ⚙️  Executed: {cmd[0]} -> {os.path.basename(log_file)}")


def compile_pipeline(manifest_path: str):
    # 0. Setup
    print(f"🚀 Starting V&V Compilation Cycle...")
    
    # 1. Parse Manifest
    sps_file = manifest_path
    output_path = None  # <--- Initialize

    if manifest_path.endswith(".yaml") or manifest_path.endswith(".yml"):
        with open(manifest_path, "r") as f:
            config = yaml.safe_load(f)
        
        sps_file = config.get("inputs", {}).get("primary_logic")
        # EXTRACT THE OUTPUT PATH
        output_path = config.get("output", {}).get("path") 

    dist_dir = "dist"
    artifacts = ArtifactManager(dist_dir)
    
    with open(sps_file, "r") as f:
        sps_code = f.read()

    # --- STAGE 1: Source Verification (PSPP) ---
    print("\n[Stage 1] Source Verification")
    run_command(
        ["pspp", sps_file], 
        os.path.join(artifacts.verification_dir, "01_source_verification.txt")
    )

    # --- STAGE 2: Parse & Build ---
    print("\n[Stage 2] Parsing & Raw Topology")
    parser = SpssParser()
    ast = parser.parse(sps_code)
    
    builder = GraphBuilder(metadata={"generator": "V&V Compiler"})
    raw_pipeline = builder.build(ast)
    
    artifacts.save_topology("02_raw_topology.yaml", raw_pipeline)

    # --- STAGE 3: Optimization ---
    print("\n[Stage 3] Optimization")
    optimizer = OptimizationCoordinator()
    optimized_pipeline = optimizer.optimize(raw_pipeline)
    
    artifacts.save_topology("03_optimized_topology.yaml", optimized_pipeline)
    
    print(f"  📉 Compression: {len(raw_pipeline.operations)} ops -> {len(optimized_pipeline.operations)} ops")

    # --- STAGE 4: Code Generation ---
    print("\n[Stage 4] Code Generation")
    generator = RGenerator(optimized_pipeline)
    r_code = generator.generate()
    
    # DECIDE WHERE TO WRITE
    dist_dir = "dist" # Default local folder
    if output_path:
        final_r_path = output_path
        # Ensure parent folder exists (e.g., project/dist/)
        os.makedirs(os.path.dirname(final_r_path), exist_ok=True)
    else:
        final_r_path = os.path.join(dist_dir, "pipeline.R")

    print(f"  💾 Writing Final R Script to: {final_r_path}")
    with open(final_r_path, "w") as f:
        f.write(r_code)



    
    r_filename = "04_generated_code.R"
    r_path = os.path.join(dist_dir, "pipeline.R") 
    
    artifacts.save_text(r_filename, r_code)
    with open(r_path, "w") as f:
        f.write(r_code)

    # --- STAGE 5: Target Verification ---
    print("\n[Stage 5] Target Verification (R Execution)")
    run_command(
        ["Rscript", r_path], 
        os.path.join(artifacts.verification_dir, "05_target_verification.txt")
    )

    print("\n✅ V&V Cycle Complete.")

# --- CLI ENTRY POINT ---
@click.command()
@click.option('--manifest', required=True, help='Path to manifest file (.yaml) or direct SPSS script (.sps)')
def build(manifest):
    """
    Entry point for the compiler CLI.
    """
    try:
        compile_pipeline(manifest)
    except Exception as e:
        print(f"❌ Compiler Error: {e}")
        # Re-raise so Pytest sees the failure
        raise e

if __name__ == "__main__":
    build()