import json
from pathlib import Path

import pytest

from converter import convert, load_units, parse_value
from errors import ConvertError


def test_length() -> None:
    assert convert(1000, "mm", "m") == 1
    assert convert(1, "km", "m") == 1000
    assert convert(250, "cm", "m") == 2.5


def test_mass() -> None:
    assert convert(1.5, "kg", "g") == 1500
    assert convert(500, "g", "kg") == 0.5


def test_result_is_float() -> None:
    assert type(convert(1000, "mm", "m")) is float


def test_temperature() -> None:
    assert convert(0, "c", "f") == 32
    assert convert(100, "c", "f") == 212
    assert convert(-40, "c", "f") == -40
    assert convert(-273.15, "c", "k") == pytest.approx(0)
    assert convert(-459.67, "f", "k") == pytest.approx(0)


def test_upper_case_units() -> None:
    assert convert(1, "KM", "M") == 1000
    assert convert(0, "C", "F") == 32


def test_below_absolute_zero() -> None:
    with pytest.raises(ConvertError, match="абсолютного нуля"):
        convert(-300, "c", "k")
    with pytest.raises(ConvertError, match="абсолютного нуля"):
        convert(-1, "k", "c")


def test_incompatible_units() -> None:
    with pytest.raises(ConvertError, match="несовместимые"):
        convert(1, "kg", "m")


def test_unknown_unit() -> None:
    with pytest.raises(ConvertError, match="неизвестная единица"):
        convert(1, "mile", "m")


@pytest.mark.parametrize("text", ["abc", "", "1,5", "nan", "inf"])
def test_bad_value(text: str) -> None:
    with pytest.raises(ConvertError, match="неверное числовое значение"):
        parse_value(text)


# ---------- бонус: таблица единиц из конфига ----------


def test_units_loaded_from_json() -> None:
    units = load_units()
    assert units["length"]["km"] == 1000
    assert "kg" in units["mass"]
    assert units["temperature"] == ["c", "f", "k"]


def test_custom_units_file(tmp_path: Path) -> None:
    config = {"length": {"m": 1, "dm": 0.1}, "mass": {"kg": 1}, "temperature": []}
    path = tmp_path / "my_units.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    assert convert(2, "m", "dm", load_units(path)) == 20


def test_broken_units_file(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("{ это не json", encoding="utf-8")
    with pytest.raises(ConvertError, match="таблицу единиц"):
        load_units(path)
