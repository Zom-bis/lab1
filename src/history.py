"""История успешных вычислений в JSON-файле.

Файл — это список записей {"expression", "result", "time"}.
Где лежит файл: путь из переменной окружения TOOLKIT_HISTORY,
а если её нет — .toolkit_history.json в домашней папке пользователя.
"""

import json
import os
from datetime import datetime
from pathlib import Path

from errors import HistoryError


def history_path() -> Path:
    path = os.environ.get("TOOLKIT_HISTORY")
    if path:
        return Path(path)
    return Path.home() / ".toolkit_history.json"


def load_history(path: Path) -> list[dict]:
    """Прочитать историю. Если файла ещё нет — история пустая."""
    if not path.exists():
        return []
    try:
        records = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise HistoryError(f"файл истории {path} повреждён") from None
    if not isinstance(records, list):
        raise HistoryError(f"файл истории {path} повреждён")
    for record in records:
        if not isinstance(record, dict) or "expression" not in record or "result" not in record:
            raise HistoryError(f"файл истории {path} повреждён")
        # в старом формате время называлось "timestamp"; если времени нет совсем — пустая строка
        record.setdefault("time", record.get("timestamp", ""))
    return records


def save_history(expression: str, result: str, path: Path) -> None:
    """Дописать одно успешное вычисление в конец истории."""
    records = load_history(path)
    records.append(
        {
            "expression": expression,
            "result": result,
            "time": datetime.now().isoformat(timespec="seconds"),
        }
    )
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


def clear_history(path: Path) -> None:
    path.write_text("[]", encoding="utf-8")
