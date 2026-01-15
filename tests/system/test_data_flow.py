import pytest
from etl_ir.model import Pipeline
from spec_generator.importers.spss.parser import SpssParser
from spec_generator.importers.spss.graph_builder import GraphBuilder
from etl_optimizer.coordinator import OptimizationCoordinator
from etl_r_generator.transpiler import RTranspiler

# ... previous imports ...
# 🟢 CHANGE: Import RGenerator, not just Transpiler
from etl_r_generator.builder import RGenerator 

class TestCompilerDataFlow:
    # ... tests 1 and 2 can stay the same ...

    def test_generator_output(self):
        """
        Step 3: Can the Generator turn IR into a String?
        """
        pipeline = Pipeline(
            metadata={"id": "optimized"}, 
            datasets=[], 
            operations=[]
        )

        # 🟢 FIX: Use RGenerator
        generator = RGenerator()
        code = generator.generate(pipeline) # .generate() not .transpile()

        assert isinstance(code, str)
        assert "library(tidyverse)" in code
        print("✅ Step 3 (IR -> R Code): Success")

    def test_the_golden_thread(self):
        """
        The Full Chain in Memory (No Disk I/O)
        """
        # 1. Input
        code = "DATA LIST FREE / id (F8.0). COMPUTE x = 1."
        
        # 2. Parse
        parser = SpssParser()
        ast = parser.parse(code)
        
        # 3. Build
        builder = GraphBuilder(metadata={"project": "golden_thread"})
        pipeline = builder.build(ast)
        
        # 4. Optimize
        optimizer = OptimizationCoordinator()
        opt_pipeline = optimizer.optimize(pipeline)
        
        # 5. Generate
        # 🟢 FIX: Use RGenerator
        generator = RGenerator()
        r_script = generator.generate(opt_pipeline)
        
        # 6. Verify
        # Check for the transpiled logic
        assert "x = 1" in r_script or "mutate(x = 1)" in r_script
        print("✅ Step 4 (The Golden Thread): Complete Compilation Cycle")



class TestCompilerDataFlow:
    """
    The 'Halfway House': 
    Verifies that the output of one component is valid input for the next.
    """

    def test_parser_to_ir_conversion(self):
        """
        Step 1: Can we turn a String into an IR Pipeline?
        """
        # 1. Source Logic
        spss_code = "COMPUTE x = 1."

        # 2. Parse (String -> AST)
        parser = SpssParser()
        ast = parser.parse(spss_code)
        assert len(ast) > 0, "Parser returned empty AST"

        # 3. Build (AST -> IR Pipeline)
        # We assume GraphBuilder takes the AST and some metadata
        builder = GraphBuilder(metadata={"project": "test_flow"})
        pipeline = builder.build(ast)

        # 4. Verify Protocol
        assert isinstance(pipeline, Pipeline), "Builder did not return a Pipeline object"
        assert pipeline.metadata.get("project") == "test_flow"
        print("\n✅ Step 1 (Parse -> IR): Success")

    def test_optimizer_pass(self):
        """
        Step 2: Can the Optimizer accept and return a Pipeline?
        """
        # Create a dummy pipeline to feed it
        pipeline = Pipeline(
            metadata={"id": "raw"}, 
            datasets=[], 
            operations=[]
        )

        coordinator = OptimizationCoordinator()
        # This will trigger the chain: Promoter -> Collapser -> Validator
        optimized_pipeline = coordinator.optimize(pipeline)

        # Verify it passed through
        assert isinstance(optimized_pipeline, Pipeline)
        print("✅ Step 2 (IR -> Optimized IR): Success")

    def test_generator_output(self):
        """
        Step 3: Can the Generator turn IR into a String?
        """
        pipeline = Pipeline(
            metadata={"id": "optimized"}, 
            datasets=[], 
            operations=[]
        )

        # 🟢 FIX: Pass pipeline to Constructor
        generator = RGenerator(pipeline)
        code = generator.generate() # No arguments here

        assert isinstance(code, str)
        assert "library(tidyverse)" in code
        print("✅ Step 3 (IR -> R Code): Success")


    def test_the_golden_thread(self):
        """
        The Full Chain in Memory (No Disk I/O)
        """
        # 1. Input
        code = "DATA LIST FREE / id (F8.0). COMPUTE x = 1."
        
        # 2. Parse
        parser = SpssParser()
        ast = parser.parse(code)
        
        # 3. Build
        builder = GraphBuilder(metadata={"project": "golden_thread"})
        pipeline = builder.build(ast)
        
        
        # 4. Optimize
        optimizer = OptimizationCoordinator()
        opt_pipeline = optimizer.optimize(pipeline)
        
        # 5. Generate
        # 🟢 FIX: Pass pipeline to Constructor
        generator = RGenerator(opt_pipeline)
        r_script = generator.generate()
        
        # 6. Verify
        assert "x = 1" in r_script or "mutate(x = 1)" in r_script
        print("✅ Step 4 (The Golden Thread): Complete Compilation Cycle")