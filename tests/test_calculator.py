from decimal import Decimal

import pytest

from calculator import calculate, format_number, rpn_string, tokenization, validation
from errors import CalcError

# ---------- позитивные тесты ----------


def test_priority() -> None:
    assert calculate("2+3*4") == 14


def test_division_gives_fraction() -> None:
    assert calculate("10 / 4") == Decimal("2.5")


def test_unary_minus_after_operator() -> None:
    assert calculate("2 * -3") == -6


def test_plus_then_unary_minus() -> None:
    assert calculate("1+-2") == -1


def test_unary_at_start() -> None:
    assert calculate("-5 + 2") == -3
    assert calculate("+7") == 7


def test_spaces_are_ignored() -> None:
    assert calculate("  1 +   2 ") == 3


def test_float_numbers() -> None:
    assert calculate("1.5 * 2") == 3


def test_left_to_right() -> None:
    assert calculate("10 - 4 - 3") == 3
    assert calculate("100 / 10 / 5") == 2


def test_tokenization() -> None:
    assert tokenization(" 12 // (3.5) ") == ["12", "//", "(", "3.5", ")"]


def test_validation_marks_unary_minus() -> None:
    assert validation(["2", "*", "-", "3"]) == ["2", "*", "~", "3"]


# ---------- бонус: // и % с отрицательными числами ----------


def test_integer_division_and_remainder() -> None:
    # // отбрасывает дробную часть, % имеет знак делимого
    assert calculate("7 // 2") == 3
    assert calculate("-7 // 2") == -3
    assert calculate("7 // -2") == -3
    assert calculate("-7 // -2") == 3
    assert calculate("-7 % 2") == -1
    assert calculate("7 % -2") == 1
    assert calculate("7.5 % 2") == Decimal("1.5")


def test_divmod_rule() -> None:
    # для любых знаков: a == b * (a // b) + a % b
    for a, b in [(7, 2), (-7, 2), (7, -2), (-7, -2)]:
        assert calculate(f"{b} * ({a} // {b}) + {a} % {b}") == a


# ---------- бонус: Decimal ----------


def test_decimal_has_no_float_error() -> None:
    assert calculate("0.1 + 0.2") == Decimal("0.3")


def test_decimal_rounding_policy() -> None:
    # 28 значащих цифр, последняя округляется по ROUND_HALF_EVEN
    assert calculate("2 / 3") == Decimal("0.6666666666666666666666666667")


def test_format_number() -> None:
    assert format_number(Decimal("2.50")) == "2.5"
    assert format_number(Decimal("1E+2")) == "100"
    assert format_number(calculate("0 * -1")) == "0"


# ---------- бонус: скобки (рекурсивный спуск) ----------


def test_parentheses() -> None:
    assert calculate("(2 + 3) * 4") == 20
    assert calculate("2 * (3 + 4) * 5") == 70
    assert calculate("-(2 + 3)") == -5
    assert calculate("((1))") == 1
    assert calculate("(1 + (2 * (3 + 4)))") == 15


# ---------- бонус: RPN ----------


def test_rpn() -> None:
    assert rpn_string("2+3*4") == "2 3 4 * +"
    assert rpn_string("1 + 2 + 3 + 4 * 8") == "1 2 + 3 + 4 8 * +"
    assert rpn_string("2*-3") == "2 3 ~ *"
    assert rpn_string("(1+2)*3") == "1 2 + 3 *"


# ---------- негативные тесты ----------


@pytest.mark.parametrize(
    ("expression", "message"),
    [
        ("", "пустое выражение"),
        ("   ", "пустое выражение"),
        ("2+a", "недопустимый символ"),
        ("2*/3", "два оператора подряд"),
        ("2*+-3", "два оператора подряд"),
        ("2+", "пропущен операнд"),
        ("*3", "пропущен операнд"),
        ("(*3)", "пропущен операнд"),
        ("2 3", "пропущен оператор"),
        ("2(3)", "пропущен оператор"),
        ("1.2.3", "неверное число"),
        ("()", "пустые скобки"),
        ("(2+3", "не закрыта скобка"),
        ("2+3)", "лишняя закрывающая скобка"),
        ("1/0", "деление на ноль"),
        ("1/(2-2)", "деление на ноль"),
        ("5 // 0", "деление на ноль"),
    ],
    ids=[
        "empty",
        "spaces",
        "bad-symbol",
        "two-operators",
        "two-unary",
        "no-right-operand",
        "no-left-operand",
        "no-operand-in-brackets",
        "no-operator",
        "no-operator-before-bracket",
        "bad-number",
        "empty-brackets",
        "unclosed-bracket",
        "extra-bracket",
        "zero-division",
        "zero-in-brackets",
        "zero-floor-division",
    ],
)
def test_errors(expression: str, message: str) -> None:
    with pytest.raises(CalcError, match=message):
        calculate(expression)


def test_too_deep_brackets() -> None:
    with pytest.raises(CalcError, match="вложенных скобок"):
        calculate("(" * 200 + "1" + ")" * 200)
