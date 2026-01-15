import pytest
from pathlib import Path
import subprocess
import yaml

# Integration tests usually invoke the CLI or the main entry point
from src.compiler import build
from click.testing import CliRunner

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
        
        # Create Manifest (Direction 1)
        manifest_file = project_dir / "compiler.yaml"
        config = {
            "project": "Integration Test",
            "inputs": {"primary_logic": str(spss_file)},
            "output": {
                "target": "r_script",
                "path": str(project_dir / "dist" / "script.R")
            }
        }
        manifest_file.write_text(yaml.dump(config))
        
        # 2. Run the Compiler
        runner = CliRunner()
        # We invoke the click command directly
        result = runner.invoke(build, ['--manifest', str(manifest_file)])
        
        # 3. Verify Success
        assert result.exit_code == 0, f"Compiler failed: {result.output}"
        
        # 4. Verify Artifacts
        output_r = project_dir / "dist" / "script.R"
        assert output_r.exists()
        
        content = output_r.read_text()
        # Check for traces of all 3 components:
        assert "load_csv" in content or "read.csv" in content # Generator worked
        assert "mutate" in content # Parser + Builder worked
        # (Optional) Check for optimization artifacts if relevant