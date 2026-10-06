from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def temp_history(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Каждый тест пишет историю во временную папку, а не в домашнюю."""
    path = tmp_path / "history.json"
    monkeypatch.setenv("TOOLKIT_HISTORY", str(path))
    return path
