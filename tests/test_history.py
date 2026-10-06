import json
from pathlib import Path

import pytest

from errors import HistoryError
from history import clear_history, load_history, save_history


def test_empty_when_no_file(tmp_path: Path) -> None:
    assert load_history(tmp_path / "nothing.json") == []


def test_save_and_load(tmp_path: Path) -> None:
    path = tmp_path / "h.json"
    save_history("2+2", "4", path)
    save_history("10/4", "2.5", path)
    records = load_history(path)
    assert [r["expression"] for r in records] == ["2+2", "10/4"]
    assert records[1]["result"] == "2.5"
    assert isinstance(json.loads(path.read_text(encoding="utf-8")), list)


def test_clear(tmp_path: Path) -> None:
    path = tmp_path / "h.json"
    save_history("1+1", "2", path)
    clear_history(path)
    assert load_history(path) == []


def test_broken_file(tmp_path: Path) -> None:
    path = tmp_path / "h.json"
    path.write_text("{сломано", encoding="utf-8")
    with pytest.raises(HistoryError):
        load_history(path)
