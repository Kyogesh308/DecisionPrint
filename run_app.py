"""
DecisionPrint — Root launcher for the dynamic Streamlit UI.

Run with:   .venv/Scripts/python.exe -m streamlit run run_app.py

Placing this at the project root (not inside ui/) prevents Streamlit from
auto-discovering ui/pages/* and avoids the multi-page conflicts.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent))

# Execute the actual app module directly
import runpy
runpy.run_module("ui.app", run_name="__main__", alter_sys=True)
