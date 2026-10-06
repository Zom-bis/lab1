"""Конвертер величин: длина, масса, температура.

Таблица единиц хранится в файле units.json рядом с этим модулем:
  "length" и "mass" — множитель к базовой единице (метру и килограмму);
  "temperature" — список температурных единиц.
Чтобы добавить единицу длины, достаточно дописать её в units.json.

Длину и массу переводим через базовую единицу: value * множитель «откуда»
и делим на множитель «куда». Температуру переводим через градусы Цельсия.

Здесь нет print и input: функции только возвращают результат
или выбрасывают ConvertError.
"""

import json
import math
from pathlib import Path

from errors import ConvertError

UNITS_FILE = Path(__file__).parent / "units.json"
ABSOLUTE_ZERO_C = -273.15


def load_units(path: Path = UNITS_FILE) -> dict:
    """Прочитать таблицу единиц из JSON-файла."""
    try:
        units = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ConvertError(f"не удалось прочитать таблицу единиц: {error}") from None
    for key in ("length", "mass", "temperature"):
        if key not in units:
            raise ConvertError(f"в таблице единиц нет раздела '{key}'")
    return units


def parse_value(text: str) -> float:
    """Превратить строку в число; nan и inf тоже считаются ошибкой."""
    try:
        value = float(text)
    except ValueError:
        raise ConvertError(f"неверное числовое значение '{text}'") from None
    if not math.isfinite(value):
        raise ConvertError(f"неверное числовое значение '{text}'")
    return value


def unit_group(unit: str, units: dict) -> str:
    """Узнать группу единицы: length, mass или temperature."""
    for group in ("length", "mass", "temperature"):
        if unit in units[group]:
            return group
    raise ConvertError(f"неизвестная единица '{unit}'")


def to_celsius(value: float, unit: str) -> float:
    if unit == "c":
        return value
    if unit == "f":
        return (value - 32) * 5 / 9
    return value + ABSOLUTE_ZERO_C  # из кельвинов


def from_celsius(value: float, unit: str) -> float:
    if unit == "c":
        return value
    if unit == "f":
        return value * 9 / 5 + 32
    return value - ABSOLUTE_ZERO_C  # в кельвины


def convert(value: float, from_unit: str, to_unit: str, units: dict | None = None) -> float:
    """Перевести value из from_unit в to_unit. Регистр единиц не важен."""
    if units is None:
        units = load_units()
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()

    group = unit_group(from_unit, units)
    if unit_group(to_unit, units) != group:
        raise ConvertError(f"несовместимые единицы: {from_unit} и {to_unit}")

    if group == "temperature":
        celsius = to_celsius(value, from_unit)
        # маленький допуск из-за погрешности float: -459.67 f — это ровно абсолютный ноль
        if celsius < ABSOLUTE_ZERO_C - 1e-9:
            raise ConvertError("температура ниже абсолютного нуля")
        result = from_celsius(celsius, to_unit)
    else:
        factors = units[group]
        result = value * factors[from_unit] / factors[to_unit]

    return float(round(result, 10))
