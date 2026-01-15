import yaml
import click
from pathlib import Path

# 🟢 The New Imports (From your bolt-on libraries)
from spec_generator.parser import SpssParser
from spec_generator.graph_builder import GraphBuilder
from etl_optimizer.coordinator import OptimizationCoordinator
from generator.transpiler import RTranspiler
# Future: from generator.excel import ExcelRulesGenerator 

@click.command()
@click.option('--manifest', default='compiler.yaml', help='Path to project manifest')
def build(manifest):
    """
    Enterprise Compiler: Bolts components together based on config.
    """
    # 1. Load Config (Direction 1)
    config = yaml.safe_load(Path(manifest).read_text())
    
    input_path = Path(config['inputs']['primary_logic'])
    output_target = config['output']['target'] # e.g., 'r_script' or 'excel_rules'
    
    print(f"🚀 Compiling {input_path} -> {output_target}...")

    # 2. Ingest (spec_generator)
    print("   [1/4] Parsing SPSS...")
    parser = SpssParser()
    # Read file content
    code = input_path.read_text()
    ast = parser.parse(code)
    
    # Build Initial Graph
    builder = GraphBuilder()
    pipeline = builder.build(ast)

    # 3. Optimize (etl_optimizer)
    print("   [2/4] Optimizing Topology...")
    optimizer = OptimizationCoordinator()
    # You might need to adjust the optimizer signature to accept the Pipeline object
    optimized_pipeline = optimizer.optimize(pipeline)

    # 4. Generate (etl-r-generator)
    print(f"   [3/4] Generating Artifacts ({output_target})...")
    
    if output_target == 'r_script':
        transpiler = RTranspiler()
        # We need to make sure RTranspiler accepts the Pipeline object directly
        # or we use the Builder pattern from the generator repo
        output_code = transpiler.transpile(optimized_pipeline)
        
        out_file = Path(config['output']['path'])
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(output_code)
        
    elif output_target == 'rules_engine_excel':
        print("   ⚠️ Excel Generator not yet implemented (Direction 3)")
    
    print("✅ Build Complete.")

if __name__ == '__main__':
    build()