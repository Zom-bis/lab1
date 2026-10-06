

from decimal import ROUND_HALF_EVEN, Decimal, DecimalException, localcontext

from constants import (
    ADD_OPERATORS,
    DIGITS,
    MAX_DEPTH,
    MUL_OPERATORS,
    OPERATORS,
    PRECISION,
    UNARY_MINUS,
)
from errors import CalcError


def tokenization(expression: str) -> list[str]:
    """Разбить строку на числа, операторы и скобки. Пробелы пропускаются."""
    tokens = []
    number = ""
    i = 0
    while i < len(expression):
        symbol = expression[i]
        if symbol in DIGITS:
            number += symbol
        else:
            # число закончилось — сохраняем его
            if number:
                tokens.append(number)
                number = ""
            if symbol == " ":
                pass
            elif expression[i : i + 2] == "//":
                tokens.append("//")
                i += 1  # второй символ "/" уже обработан
            elif symbol in OPERATORS or symbol in "()":
                tokens.append(symbol)
            else:
                raise CalcError(f"недопустимый символ '{symbol}'")
        i += 1
    if number:
        tokens.append(number)
    return tokens


def is_number(token: str) -> bool:
    return token[0] in DIGITS


def validation(tokens: list[str]) -> list[str]:

    if not tokens:
        raise CalcError("пустое выражение")

    result = []
    expect_number = True  # в начале выражения ждём число
    unary_used = False  # был ли уже унарный знак перед этим числом
    depth = 0

    for token in tokens:
        if expect_number:
            if is_number(token):
                try:
                    Decimal(token)
                except DecimalException:
                    raise CalcError(f"неверное число '{token}'") from None
                result.append(token)
                expect_number = False
                unary_used = False
            elif token == "(":
                depth += 1
                if depth > MAX_DEPTH:
                    raise CalcError("слишком много вложенных скобок")
                result.append(token)
                unary_used = False
            elif token in ("+", "-") and not unary_used:
                if token == "-":
                    result.append(UNARY_MINUS)
                unary_used = True
            elif token == ")":
                if result and result[-1] == "(":
                    raise CalcError("пустые скобки")
                raise CalcError("пропущен операнд перед ')'")
            elif (not result or result[-1] == "(") and not unary_used:
                raise CalcError(f"пропущен операнд перед '{token}'")
            else:
                raise CalcError(f"два оператора подряд перед '{token}'")
        else:
            if is_number(token) or token == "(":
                raise CalcError(f"пропущен оператор перед '{token}'")
            if token == ")":
                if depth == 0:
                    raise CalcError("лишняя закрывающая скобка")
                depth -= 1
            else:
                expect_number = True
            result.append(token)

    if expect_number:
        raise CalcError("пропущен операнд в конце выражения")
    if depth > 0:
        raise CalcError("не закрыта скобка")
    return result


class RpnParser:
    def __init__(self, tokens: list[str]) -> None:
        self.tokens = tokens
        self.pos = 0  # номер текущего токена
        self.output: list[str] = []

    def current(self) -> str | None:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def expression(self) -> None:
        self.term()
        while self.current() in ADD_OPERATORS:
            operator = self.tokens[self.pos]
            self.pos += 1
            self.term()
            self.output.append(operator)

    def term(self) -> None:
        self.unary()
        while self.current() in MUL_OPERATORS:
            operator = self.tokens[self.pos]
            self.pos += 1
            self.unary()
            self.output.append(operator)

    def unary(self) -> None:
        if self.current() == UNARY_MINUS:
            self.pos += 1
            self.primary()
            self.output.append(UNARY_MINUS)
        else:
            self.primary()

    def primary(self) -> None:
        token = self.current()
        if token == "(":
            self.pos += 1
            self.expression()
            self.pos += 1  # пропускаем ")", validation уже проверила, что она есть
        else:
            self.output.append(token)
            self.pos += 1


def to_rpn(tokens: list[str]) -> list[str]:
    """Перевести проверенные токены в обратную польскую запись."""
    parser = RpnParser(tokens)
    parser.expression()
    return parser.output


def apply_operator(a: Decimal, b: Decimal, operator: str) -> Decimal:
    """Выполнить одну бинарную операцию."""
    if operator in ("/", "//", "%") and b == 0:
        raise CalcError("деление на ноль")
    if operator == "+":
        return a + b
    if operator == "-":
        return a - b
    if operator == "*":
        return a * b
    if operator == "/":
        return a / b
    # // отбрасывает дробную часть (округление к нулю): -7 // 2 = -3.
    # % — остаток со знаком делимого: -7 % 2 = -1. Так Decimal и считает.
    if operator == "//":
        return a // b
    return a % b


def calculation(rpn: list[str]) -> Decimal:
    """Вычислить выражение в RPN с помощью стека."""
    stack = []
    with localcontext() as context:
        context.prec = PRECISION
        context.rounding = ROUND_HALF_EVEN
        for token in rpn:
            if token == UNARY_MINUS:
                stack.append(-stack.pop())
            elif token in OPERATORS:
                b = stack.pop()  # правый операнд лежит сверху
                a = stack.pop()
                stack.append(apply_operator(a, b, token))
            else:
                stack.append(Decimal(token))
    return stack[0]


def calculate(expression: str) -> Decimal:
    """Посчитать выражение целиком: все четыре шага подряд."""
    tokens = tokenization(expression)
    checked = validation(tokens)
    rpn = to_rpn(checked)
    return calculation(rpn)


def rpn_string(expression: str) -> str:
    """RPN выражения в виде строки, например '2 3 4 * +'."""
    return " ".join(to_rpn(validation(tokenization(expression))))


def format_number(value: Decimal) -> str:
    """Decimal('14') -> '14', Decimal('2.50') -> '2.5', без экспоненты."""
    if value == 0:
        return "0"  # убираем "-0"
    return format(value.normalize(), "f")
