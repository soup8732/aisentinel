from __future__ import annotations

from pathlib import Path
from src.utils.config import load_config


def test_load_config_defaults(tmp_path: Path) -> None:
    cfg = load_config()
    assert cfg.environment in {"development", "staging", "production"}
    # Paths resolve to directories even if they don't exist yet
    assert "data" in str(cfg.paths.data_dir)
