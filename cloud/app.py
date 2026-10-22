"""Community Cloud entry point. Keeps the local prototype's same UI and engine."""
import os
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["AIMSCRIBE_CLOUD"] = "1"

runpy.run_path(str(ROOT / "app.py"), run_name="__main__")
