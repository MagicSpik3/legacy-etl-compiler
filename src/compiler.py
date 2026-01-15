import yaml
import click
from pathlib import Path

# 1. Imports
from etl_ir.model import Pipeline
from spec_generator.importers.spss.parser import SpssParser
from spec_generator.importers.spss.graph_builder import GraphBuilder
from etl_optimizer.coordinator import OptimizationCoordinator
# 🟢 CHANGE: Import RGenerator, not RTranspiler
from etl_r_generator.builder import RGenerator

@click.command()
@click.option('--manifest', default='compiler.yaml', help='Path to project manifest')
def build(manifest):
    """
    The Enterprise Compiler CLI
    """
    manifest_path = Path(manifest)
    if not manifest_path.exists():
        click.echo(f"❌ Manifest not found: {manifest}")
        return

    # 1. Load Config
    with open(manifest_path) as f:
        config = yaml.safe_load(f)

    spss_path = config['inputs']['primary_logic']
    output_path = config['output']['path']
    target_lang = config['output']['target']

    click.echo(f"🚀 Compiling {spss_path} -> {target_lang}...")

    try:
        # --- Step 1: Parsing ---
        click.echo("    [1/4] Parsing SPSS...")
        with open(spss_path, 'r') as f:
            source_code = f.read()
        
        parser = SpssParser()
        ast = parser.parse(source_code)
        
        # Build Initial IR
        # 🟢 FIX: Pass config as metadata to GraphBuilder
        builder = GraphBuilder(metadata=config)
        pipeline = builder.build(ast)

        # --- Step 2: Optimization ---
        click.echo("    [2/4] Optimizing Topology...")
        optimizer = OptimizationCoordinator()
        optimized_pipeline = optimizer.optimize(pipeline)

        # --- Step 3: Code Generation ---
        click.echo(f"    [3/4] Generating Artifacts ({target_lang})...")
        
        if target_lang == 'r_script':
            # 🟢 FIX: Use RGenerator(pipeline)
            generator = RGenerator(optimized_pipeline)
            output_code = generator.generate()
        else:
            raise NotImplementedError(f"Target language '{target_lang}' not supported")

        # --- Step 4: Write Output ---
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(output_code)
        
        click.echo(f"✅ Success! Compiled to: {output_path}")

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")
        # Re-raise so Click sees the non-zero exit code during tests
        raise e

if __name__ == '__main__':
    build()