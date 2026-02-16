import pytest
import importlib

# The list of packages that MUST be present for the compiler to work
REQUIRED_PACKAGES = [
    "etl_ir",
    "spec_generator",
    "etl_optimizer",
    "etl_r_generator"
]

class TestEnvironmentSanity:
    
    @pytest.mark.parametrize("package_name", REQUIRED_PACKAGES)
    def test_package_is_importable(self, package_name):
        """
        Level 1: Can we even see the code?
        """
        try:
            mod = importlib.import_module(package_name)
            print(f"✅ Imported {package_name} from: {mod.__file__}")
        except ImportError as e:
            pytest.fail(f"❌ CRITICAL: Could not import '{package_name}'. Is the venv active? {e}")

    @pytest.mark.parametrize("package_name", REQUIRED_PACKAGES)
    def test_package_has_version(self, package_name):
        """
        Level 2: Do we know WHICH version we are running?
        This forces you to maintain a __version__ in your packages.
        """
        mod = importlib.import_module(package_name)
        
        # Check for __version__ attribute
        version = getattr(mod, "__version__", None)
        
        if version is None:
            pytest.fail(
                f"❌ Package '{package_name}' has no version number.\n"
                f"   Action: Add `__version__ = '0.1.0'` to {package_name}/__init__.py"
            )
        
        print(f"ℹ️  {package_name} Version: {version}")
        assert isinstance(version, str), "Version should be a string (e.g., '1.0.0')"