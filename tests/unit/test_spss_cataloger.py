import os
import tempfile

from src.spss_cataloger import SpssParser, SpssDirectoryCataloger


def test_extracts_input_files_and_variables_from_sps_content():
    content = """
GET DATA /TYPE=TXT /FILE='data.csv' /VARIABLES=age F2 sex A1.
COMPUTE income = salary * 1.2.
RENAME VARIABLES (oldvar = newvar).
DELETE VARIABLES unused.
VARIABLE LABELS age 'Age in years'.
RECODE score (1=10) (2=20).
"""

    parser = SpssParser()
    input_files = parser._extract_input_files(content)
    variables = parser._extract_variables(content)

    assert 'data.csv' in input_files
    assert 'income' in variables
    assert 'age' in variables
    assert 'newvar' in variables
    assert 'oldvar' in variables
    assert 'unused' in variables
    assert 'score' in variables


def test_new_variable_flag_from_input_variables():
    content = """
GET DATA /TYPE=TXT /FILE='data.csv' /VARIABLES=age F2 sex A1.
COMPUTE income = salary * 1.2.
COMPUTE age = age + 1.
STRING newflag (A1).
"""

    parser = SpssParser()
    input_vars = parser._extract_input_variables(content)
    assert 'age' in input_vars
    assert 'sex' in input_vars

    created = parser._extract_created_variables(content, input_vars)

    assert 'income' in created
    assert 'newflag' in created
    assert 'age' not in created
    assert 'sex' not in created


def test_catalog_path_parses_single_sps_file(tmp_path):
    sample_content = """
GET FILE = 'input.sav'.
COMPUTE z = x + y.
"""
    sample_file = tmp_path / 'sample.sps'
    sample_file.write_text(sample_content, encoding='utf-8')

    cataloger = SpssDirectoryCataloger()
    metadata_list = cataloger.catalog_path(str(sample_file), recursive=False)

    assert len(metadata_list) == 1
    metadata = metadata_list[0]
    assert metadata.filename == 'sample.sps'
    assert 'input.sav' in metadata.input_files
    assert 'z' in metadata.variables
