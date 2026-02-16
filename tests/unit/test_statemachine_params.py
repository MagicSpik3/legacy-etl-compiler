import pytest
from spec_generator.importers.spss.parser import SpssParser
from etl_ir.model import Pipeline

def test_load_parameter_integrity():
    """
    Verify that GET DATA parameters (like FIRSTCASE) are correctly 
    captured in the State Machine's IR.
    """
    spss_content = """
    GET DATA
      /TYPE=TXT
      /FILE='test.csv'
      /FIRSTCASE=2
      /VARIABLES=id F8.0.
    """
    
    # 1. Parse the string (Mocking the file read)
    parser = SpssParser()
    topology = parser.parse_string(spss_content)
    
    # 2. Extract the LOAD operation
    load_op = next(op for op in topology if op.type == "LOAD_CSV")
    
    # 3. Assertions: The Map must match the Territory
    assert load_op.params['filename'] == 'test.csv'
    assert load_op.params['skip_rows'] == 1, "Failed to map FIRSTCASE=2 to skip_rows=1"
    assert 'id' in load_op.params['schema'], "Variable 'id' missing from IR schema"

def test_sort_order_persistence():
    """
    Verify that SORT CASES correctly identifies the direction (A vs D).
    """
    spss_content = "SORT CASES BY id (D)."
    
    parser = SpssParser()
    topology = parser.parse_string(spss_content)
    sort_op = next(op for op in topology if op.type == "SORT_ROWS")
    
    assert sort_op.params['keys'] == 'id'
    assert sort_op.params['order'] == 'descending'