from __future__ import annotations

import importlib


def test_dashboard_imports() -> None:
    # Ensures the Streamlit app module exists and is importable
    importlib.import_module("src.dashboard.app")
