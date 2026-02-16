import pytest
from pathlib import Path
import yaml
from click.testing import CliRunner
from src.compiler import build

# ==============================================================================
# 📜 PSPP CAPABILITY MATRIX (The "Red Light" List)
# ==============================================================================
SCENARIOS = [
    {
        "id": "01_load_sort_save",
        "spss": """
            GET DATA /TYPE=TXT /FILE='data.csv' /VARIABLES=id F3.
            SORT CASES BY id.
            SAVE OUTFILE='sorted.sav'.
        """,
        "expected_r": ["read_csv", "arrange", "write_sav"]
    },
    {
        "id": "02_missing_values",
        "spss": """
            GET DATA /TYPE=TXT /FILE='data.csv' /VARIABLES=age F3.
            MISSING VALUES age (-9).
            COMPUTE valid_age = age.
        """,
        "expected_r": ["na_if", "-9", "mutate"]
    },
    {
        "id": "03_compute_recode",
        "spss": """
            GET DATA /TYPE=TXT /FILE='data.csv' /VARIABLES=score F3.
            COMPUTE pass = score >= 50.
            RECODE score (0 THRU 49 = 0) (50 THRU 100 = 1) INTO grade.
        """,
        "expected_r": ["mutate", "score >= 50", "case_when", "between"]
    },
    {
        "id": "04_filter",
        "spss": """
            GET DATA /TYPE=TXT /FILE='data.csv' /VARIABLES=age F3.
            SELECT IF age >= 18.
        """,
        "expected_r": ["filter", "age >= 18"]
    },
    {
        "id": "05_lag",
        "spss": """
            GET DATA /TYPE=TXT /FILE='data.csv' /VARIABLES=val F3.
            SORT CASES BY id.
            COMPUTE prev = LAG(val).
        """,
        "expected_r": ["arrange", "mutate", "lag(val"]
    },
    {
        "id": "06_aggregate",
        "spss": """
            GET DATA /TYPE=TXT /FILE='data.csv' /VARIABLES=grp F1 score F3.
            AGGREGATE /OUTFILE=* /BREAK=grp /mean_score = MEAN(score).
        """,
        "expected_r": ["group_by", "summarise", "mean(score"]
    },
    {
        "id": "07_match_files_join",
        "spss": """
            MATCH FILES /FILE='left.sav' /FILE='right.sav' /BY id.
            SAVE OUTFILE='merged.sav'.
        """,
        "expected_r": ["left_join", "by", "id"] 
        # Note: Compiler might default to left_join or full_join depending on logic
    },
    {
        "id": "08_do_if_logic",
        "spss": """
            GET DATA /TYPE=TXT /FILE='data.csv' /VARIABLES=age F3.
            DO IF (age < 18).
                COMPUTE group = 0.
            ELSE.
                COMPUTE group = 1.
            END IF.
        """,
        "expected_r": ["mutate", "if_else", "case_when"] 
        # Note: CodeGen usually flattens DO IF into if_else() or case_when()
    },
    {
        "id": "09_string_concat",
        "spss": """
            GET DATA /TYPE=TXT /FILE='data.csv' /VARIABLES=name A10.
            STRING label (A20).
            COMPUTE label = CONCAT("ID_", name).
        """,
        "expected_r": ["mutate", "paste", "str_c", "ID_"]
    },
    {
        "id": "12_sav_roundtrip",
        "spss": """
            GET FILE='input.sav'.
            SAVE OUTFILE='output.sav'.
        """,
        "expected_r": ["read_sav", "write_sav", "haven"]
    }
]

class TestSystemIntegration:
    
    @pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda x: x["id"])
    def test_pspp_compliance(self, tmp_path, scenario):
        """
        Dynamically tests the compiler against the 'Golden List' of PSPP capabilities.
        """
        # 1. Setup Environment
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        # Write the SPSS Logic
        spss_file = project_dir / "logic.sps"
        spss_file.write_text(scenario["spss"])
        
        # Write the Manifest
        manifest_file = project_dir / "compiler.yaml"
        config = {
            "project": f"Test {scenario['id']}",
            "inputs": {"primary_logic": str(spss_file)},
            "output": {
                "target": "r_script",
                "path": str(project_dir / "dist" / "script.R")
            }
        }
        manifest_file.write_text(yaml.dump(config))
        
        # 2. Execute Compiler
        runner = CliRunner()
        result = runner.invoke(build, ['--manifest', str(manifest_file)])
        
        # 3. Assertions
        print(f"\nRunning Scenario: {scenario['id']}")
        
        # A) Did it crash?
        if result.exit_code != 0:
            print(f"❌ COMPILER CRASHED: {result.output}")
        assert result.exit_code == 0
        
        # B) Did it generate the file?
        output_r = project_dir / "dist" / "script.R"
        assert output_r.exists(), "R script was not generated"
        
        # C) Does the R code contain the expected keywords?
        content = output_r.read_text().lower() # Normalize case
        
        print(f"👇 GENERATED R ({scenario['id']}) 👇\n{content}\n")
        
        for keyword in scenario["expected_r"]:
            assert keyword.lower() in content, \
                f"Failed to find keyword '{keyword}' in generated R for scenario {scenario['id']}"