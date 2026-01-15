import pytest
from etl_ir.model import Pipeline
from spec_generator.importers.spss.parser import SpssParser
from etl_optimizer.collapser import VerticalCollapser
from etl_r_generator.transpiler import RTranspiler

class TestComponentSanity:

    def test_hello_ir(self):
        """Can we create a blank IR Pipeline?"""
        # FIX: Put 'id' inside the metadata dictionary
        pipeline = Pipeline(
            metadata={"id": "hello_world"}, 
            datasets=[], 
            operations=[]
        )
        # Assert against the metadata, not a top-level attribute
        assert pipeline.metadata["id"] == "hello_world"
        print("\n✅ Hello IR: Alive")

    def test_hello_parser(self):
        """Can the Parser digest a tiny string?"""
        parser = SpssParser()
        ast = parser.parse("COMPUTE x = 1.")
        assert ast is not None
        print("✅ Hello Parser: Alive")

    def test_hello_optimizer(self):
        """Can we instantiate the Optimizer components?"""
        # FIX: Create a dummy pipeline first, then pass it to the Optimizer constructor
        dummy_pipeline = Pipeline(id="dummy", datasets=[], operations=[])
        
        collapser = VerticalCollapser(dummy_pipeline)
        assert collapser is not None
        print("✅ Hello Optimizer: Alive")

    def test_hello_generator(self):
        """Can we instantiate the R Transpiler?"""
        transpiler = RTranspiler()
        assert transpiler is not None
        print("✅ Hello Generator: Alive")