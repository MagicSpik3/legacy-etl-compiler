import pytest
from pathlib import Path
import os
import yaml
from click.testing import CliRunner
from src.compiler import build

class TestSystemIntegration:
    
    def test_end_to_end_execution(self, tmp_path):
        """
        Verifies that we can read a manifest, find the local SPSS file,
        parse it, optimize it, and generate R code.
        """
        # 1. Setup the 'Project' environment
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        # Create Dummy SPSS
        spss_file = project_dir / "logic.sps"
        spss_file.write_text("DATA LIST FREE / id (F8.0). COMPUTE x = 1. SAVE OUTFILE='out.csv'.")
        
        # Create Manifest
        output_target = project_dir / "dist" / "script.R"
        manifest_file = project_dir / "compiler.yaml"
        config = {
            "project": "Integration Test",
            "inputs": {"primary_logic": str(spss_file)},
            "output": {
                "target": "r_script",
                "path": str(output_target) # <--- Test expects file HERE
            }
        }
        manifest_file.write_text(yaml.dump(config))
        
        # 2. Run the Compiler
        runner = CliRunner()
        result = runner.invoke(build, ['--manifest', str(manifest_file)])
        
        # 3. Verify Execution Success
        assert result.exit_code == 0, f"Compiler failed: {result.output}"
        
        # --- 🕵️ DEBUGGING BLOCK START ---
        print("\n--- DEBUG: FILE SYSTEM STATE ---")
        print(f"Expected File: {output_target}")
        
        if not output_target.exists():
            print("❌ Expected file NOT found.")
            
            # Check where the compiler actually wrote files
            cwd_dist = Path("dist")
            if cwd_dist.exists():
                print(f"Found 'dist' in Current Working Directory: {cwd_dist.absolute()}")
                print(f"Contents: {list(cwd_dist.iterdir())}")
            else:
                print("Could not find any 'dist' folder.")
        # --- DEBUGGING BLOCK END ---

        # 4. Verify Artifacts
        assert output_target.exists(), f"File missing. Check stdout for debug info."
        
        content = output_target.read_text()
        assert "read_csv" in content or "tibble" in content 
        assert "mutate" in content