import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "digital_root.py"

def test_valid_input():
    result = subprocess.run([sys.executable, str(SCRIPT), "16"], capture_output=True, text=True)
    assert result.returncode == 0
    assert result.stdout.strip() == "7"

def test_invalid_input():
    result = subprocess.run([sys.executable, str(SCRIPT), "abc"], capture_output=True, text=True)
    assert result.returncode == 1
    assert "non-negative integer" in result.stderr.lower()
