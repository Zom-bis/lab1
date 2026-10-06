import os
import subprocess
import sys
from pathlib import Path

import pytest

from history import load_history
from toolkit import main

SRC = str(Path(__file__).parent.parent / "src")


def run(*args: str, history: Path) -> subprocess.CompletedProcess:
    """Запустить python -m toolkit как отдельную программу."""
    env = {
        **os.environ,
        "PYTHONPATH": SRC,
        "PYTHONIOENCODING": "utf-8",
        "TOOLKIT_HISTORY": str(history),
    }
    return subprocess.run(
        [sys.executable, "-m", "toolkit", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )


def test_help_exit_code_0(temp_history: Path) -> None:
    result = run("--help", history=temp_history)
    assert result.returncode == 0
    assert "calc" in result.stdout


def test_error_goes_to_stderr_with_code_2(temp_history: Path) -> None:
    result = run("calc", "1/0", history=temp_history)
    assert result.returncode == 2
    assert result.stdout == ""
    assert "деление на ноль" in result.stderr


def test_calc(capsys: pytest.CaptureFixture) -> None:
    assert main(["calc", "(2+3)*4"]) == 0
    assert capsys.readouterr().out.strip() == "20"


def test_calc_rpn(capsys: pytest.CaptureFixture) -> None:
    assert main(["calc", "2*-3", "--rpn"]) == 0
    assert capsys.readouterr().out.splitlines() == ["RPN: 2 3 ~ *", "-6"]


def test_convert(capsys: pytest.CaptureFixture) -> None:
    assert main(["convert", "1000", "--from", "mm", "--to", "m"]) == 0
    assert capsys.readouterr().out.strip() == "1 m"


def test_convert_error(capsys: pytest.CaptureFixture) -> None:
    assert main(["convert", "1", "--from", "kg", "--to", "m"]) == 2
    assert "несовместимые" in capsys.readouterr().err


def test_history_saves_only_success(temp_history: Path, capsys: pytest.CaptureFixture) -> None:
    main(["calc", "2+2"])
    main(["calc", "1/0"])
    assert [r["expression"] for r in load_history(temp_history)] == ["2+2"]
    capsys.readouterr()
    assert main(["history"]) == 0
    assert "2+2 = 4" in capsys.readouterr().out
