"""Community Cloud entry point. Keeps the local prototype's same UI and engine."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["AIMSCRIBE_CLOUD"] = "1"

import app  # noqa: E402,F401: Streamlit executes the shared application on import.
