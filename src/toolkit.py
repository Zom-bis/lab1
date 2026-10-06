"""Командная строка: python -m toolkit calc / convert / history.

Только этот файл печатает на экран. Ошибки ввода выводятся
в stderr, программа завершается с кодом 2.
"""

import argparse
import sys
from pathlib import Path

from calculator import calculate, format_number, rpn_string
from converter import convert, load_units, parse_value
from errors import ToolkitError
from history import clear_history, history_path, load_history, save_history


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="toolkit",
        description="Калькулятор и конвертер величин.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    calc = commands.add_parser("calc", help="посчитать выражение")
    calc.add_argument("expression", help='выражение в кавычках, например "(2 + 3) * 4"')
    calc.add_argument("--rpn", action="store_true", help="показать обратную польскую запись")

    conv = commands.add_parser("convert", help="перевести величину в другую единицу")
    conv.add_argument("value", help="число")
    conv.add_argument("--from", dest="from_unit", required=True, help="mm cm m km g kg c f k")
    conv.add_argument("--to", dest="to_unit", required=True, help="mm cm m km g kg c f k")
    conv.add_argument("--units", help="свой JSON-файл с таблицей единиц")

    hist = commands.add_parser("history", help="показать историю вычислений")
    hist.add_argument("--clear", action="store_true", help="очистить историю")

    return parser


def run_calc(args: argparse.Namespace) -> None:
    result = format_number(calculate(args.expression))
    save_history(args.expression, result, history_path())
    if args.rpn:
        print("RPN:", rpn_string(args.expression))
    print(result)


def run_convert(args: argparse.Namespace) -> None:
    units = load_units(Path(args.units)) if args.units else load_units()
    value = parse_value(args.value)
    result = convert(value, args.from_unit, args.to_unit, units)
    if result.is_integer():
        print(int(result), args.to_unit.lower())
    else:
        print(result, args.to_unit.lower())


def run_history(args: argparse.Namespace) -> None:
    path = history_path()
    if args.clear:
        clear_history(path)
        print("История очищена")
        return
    records = load_history(path)
    if not records:
        print("История пуста")
    for record in records:
        print(f"{record['time']}  {record['expression']} = {record['result']}")


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    parser = make_parser()
    if not argv:
        parser.print_help()
        return 0
    args = parser.parse_args(argv)

    try:
        if args.command == "calc":
            run_calc(args)
        elif args.command == "convert":
            run_convert(args)
        else:
            run_history(args)
    except ToolkitError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
