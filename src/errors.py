"""Ошибки программы.

Все ошибки ввода наследуются от ToolkitError, поэтому в CLI
достаточно ловить только его.
"""


class ToolkitError(Exception):
    """Ошибка во вводе пользователя."""


class CalcError(ToolkitError):
    """Ошибка в выражении калькулятора."""


class ConvertError(ToolkitError):
    """Ошибка в конвертере величин или в таблице единиц."""


class HistoryError(ToolkitError):
    """Файл истории повреждён или не читается."""
