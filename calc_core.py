import math
import re
from typing import Any, Dict


def build_allowed_names() -> Dict[str, Any]:
    allowed: Dict[str, Any] = {}
    for name in [
        "sin",
        "cos",
        "tan",
        "asin",
        "acos",
        "atan",
        "sinh",
        "cosh",
        "tanh",
        "log",
        "log10",
        "sqrt",
        "pow",
        "exp",
        "fabs",
        "floor",
        "ceil",
        "degrees",
        "radians",
        "factorial",
        "gamma",
        "lgamma",
    ]:
        allowed[name] = getattr(math, name)
    allowed["ln"] = math.log
    allowed["abs"] = abs
    allowed.update({
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
        "inf": math.inf,
        "nan": math.nan,
    })
    return allowed


def replace_factorial_operators(expression: str) -> str:
    pattern_number = re.compile(r"(?P<val>(?:\d+(?:\.\d+)?)|(?:pi|e|tau|inf|nan))!")
    pattern_paren = re.compile(r"\)(!)+")

    prev = None
    s = expression
    while prev != s:
        prev = s
        s = pattern_number.sub(lambda m: f"factorial({m.group('val')})", s)

    while True:
        match = pattern_paren.search(s)
        if not match:
            break
        bangs = match.group(1)
        close_index = match.start()
        open_index = close_index
        depth = 0
        while open_index >= 0:
            ch = s[open_index]
            if ch == ')':
                depth += 1
            elif ch == '(':
                depth -= 1
                if depth == 0:
                    break
            open_index -= 1
        if open_index < 0:
            break
        inner = s[open_index: close_index + 1]
        wrapped = inner
        for _ in bangs:
            wrapped = f"factorial{wrapped}"
        s = s[:open_index] + wrapped + s[close_index + 1 + len(bangs):]
    return s


def preprocess_expression(expr: str) -> str:
    s = expr.strip()
    if not s:
        return s
    s = s.replace('×', '*').replace('÷', '/')
    s = s.replace('^', '**')
    s = re.sub(r"(\d+(?:\.\d+)?)%", r"(\1/100)", s)
    s = replace_factorial_operators(s)
    return s


def evaluate_expression(text: str) -> float:
    expr = preprocess_expression(text)
    if not expr:
        return 0.0
    try:
        result = eval(expr, {"__builtins__": {}}, build_allowed_names())
    except ZeroDivisionError as exc:
        raise ZeroDivisionError("Division by zero") from exc
    except Exception as exc:
        raise ValueError("Invalid expression") from exc
    if isinstance(result, (int, float)):
        return float(result)
    raise ValueError("Expression did not evaluate to a number")


