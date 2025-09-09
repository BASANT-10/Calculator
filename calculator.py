import math
import re
import sys
from typing import Dict, Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


def build_allowed_names() -> Dict[str, Any]:
    allowed: Dict[str, Any] = {}
    # math functions
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

    # aliases
    allowed["ln"] = math.log
    allowed["abs"] = abs

    # constants
    allowed.update({
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
        "inf": math.inf,
        "nan": math.nan,
    })
    return allowed


def replace_factorial_operators(expression: str) -> str:
    """Convert occurrences of x! into factorial(x).

    Supports nested and chained factorials like 5!! or (3+2)!
    """
    # Handle multiple factorials by repeatedly applying regex until stable
    pattern_number = re.compile(r"(?P<val>(?:\d+(?:\.\d+)?)|(?:pi|e|tau|inf|nan))!")
    pattern_paren = re.compile(r"\)(!)+")

    prev = None
    s = expression
    # First, numbers/constants followed by !
    while prev != s:
        prev = s
        s = pattern_number.sub(lambda m: f"factorial({m.group('val')})", s)

    # Then, closing parens followed by one or more !
    # Replace )! -> ) and wrap with factorial( ... )
    # We do this by scanning and inserting wrappers
    while True:
        match = pattern_paren.search(s)
        if not match:
            break
        bangs = match.group(1)
        # Find matching open paren for the ) at match.start()
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
            # unmatched, stop to avoid infinite loop
            break
        inner = s[open_index: close_index + 1]
        # apply factorial as many times as bangs length
        wrapped = inner
        for _ in bangs:
            wrapped = f"factorial{wrapped}"
        s = s[:open_index] + wrapped + s[close_index + 1 + len(bangs):]
    return s


def preprocess_expression(expr: str) -> str:
    s = expr.strip()
    if not s:
        return s
    # Replace unicode multiplication and division
    s = s.replace('×', '*').replace('÷', '/')
    # Replace caret with exponentiation
    s = s.replace('^', '**')
    # Percent: convert trailing % to /100
    s = re.sub(r"(\d+(?:\.\d+)?)%", r"(\1/100)", s)
    # Factorial handling
    s = replace_factorial_operators(s)
    return s


class ScientificCalculator(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Modern Scientific Calculator")
        self.allowed_names = build_allowed_names()
        self.current_theme = "dark"

        self._build_ui()
        self._apply_theme(self.current_theme)
        self._build_menu()

    def _build_menu(self) -> None:
        menu = self.menuBar().addMenu("View")
        toggle_theme_action = QAction("Toggle Dark/Light", self)
        toggle_theme_action.setShortcut(QKeySequence("Ctrl+T"))
        toggle_theme_action.triggered.connect(self.toggle_theme)
        menu.addAction(toggle_theme_action)

        clear_history_action = QAction("Clear History", self)
        clear_history_action.triggered.connect(self.history.clear)
        menu.addAction(clear_history_action)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)

        # Left side: display + keypad
        left = QVBoxLayout()
        root_layout.addLayout(left, 3)

        self.display = QLineEdit()
        self.display.setPlaceholderText("Enter expression...")
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setReadOnly(False)
        self.display.setMaxLength(512)
        self.display.returnPressed.connect(self.calculate)
        left.addWidget(self.display)

        grid = QGridLayout()
        left.addLayout(grid)

        # Right side: history panel
        right = QVBoxLayout()
        root_layout.addLayout(right, 2)
        right.addWidget(QLabel("History"))
        self.history = QListWidget()
        self.history.itemClicked.connect(self._on_history_clicked)
        right.addWidget(self.history)

        # Row definitions (text, slot, span)
        buttons = [
            # Row 0
            [("MC", self.memory_clear), ("MR", self.memory_read), ("M+", self.memory_add), ("M-", self.memory_subtract), ("CE", self.clear_entry), ("C", self.clear_all)],
            # Row 1
            [("←", self.backspace), ("(", lambda: self._insert_text("(")), (")", lambda: self._insert_text(")")), ("±", self.toggle_sign), ("%", lambda: self._insert_text("%")), ("÷", lambda: self._insert_text("÷"))],
            # Row 2
            [("7", lambda: self._insert_text("7")), ("8", lambda: self._insert_text("8")), ("9", lambda: self._insert_text("9")), ("×", lambda: self._insert_text("×")), ("x^y", lambda: self._insert_text("^")), ("x²", lambda: self.square)],
            # Row 3
            [("4", lambda: self._insert_text("4")), ("5", lambda: self._insert_text("5")), ("6", lambda: self._insert_text("6")), ("-", lambda: self._insert_text("-")), ("√", self.sqrt), ("x³", self.cube)],
            # Row 4
            [("1", lambda: self._insert_text("1")), ("2", lambda: self._insert_text("2")), ("3", lambda: self._insert_text("3")), ("+", lambda: self._insert_text("+")), ("1/x", self.reciprocal), ("x!", self.factorial)],
            # Row 5
            [("0", lambda: self._insert_text("0")), (".", lambda: self._insert_text(".")), ("π", lambda: self._insert_text("pi")), ("e", lambda: self._insert_text("e")), ("Ans", self.use_last_answer), ("=", self.calculate)],
            # Row 6 functions
            [("sin", lambda: self._insert_text("sin(")), ("cos", lambda: self._insert_text("cos(")), ("tan", lambda: self._insert_text("tan(")), ("ln", lambda: self._insert_text("ln(")), ("log", lambda: self._insert_text("log10(")), ("exp", lambda: self._insert_text("exp("))],
        ]

        # Create buttons
        for r, row in enumerate(buttons):
            for c, (text, handler) in enumerate(row):
                btn = QPushButton(text)
                btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                btn.clicked.connect(handler)
                grid.addWidget(btn, r, c)

        self.memory_value = 0.0
        self.last_answer: float | None = None

        # Keyboard shortcuts
        for key in [str(i) for i in range(10)] + ["+", "-", "*", "/", ".", "(", ")", "^"]:
            sc = QAction(self)
            sc.setShortcut(QKeySequence(key))
            sc.triggered.connect(lambda k=key: self._insert_text(k))
            self.addAction(sc)

        enter = QAction(self)
        enter.setShortcut(QKeySequence(Qt.Key.Key_Return))
        enter.triggered.connect(self.calculate)
        self.addAction(enter)

        back = QAction(self)
        back.setShortcut(QKeySequence(Qt.Key.Key_Backspace))
        back.triggered.connect(self.backspace)
        self.addAction(back)

        esc = QAction(self)
        esc.setShortcut(QKeySequence(Qt.Key.Key_Escape))
        esc.triggered.connect(self.clear_entry)
        self.addAction(esc)

    def _apply_theme(self, theme: str) -> None:
        if theme == "dark":
            self.setStyleSheet(
                """
                QMainWindow { background: #0f1115; }
                QWidget { color: #e6e6e6; font-size: 16px; }
                QLineEdit { background: #161a22; border: 1px solid #2a2f3a; padding: 10px; border-radius: 8px; font-size: 22px; }
                QPushButton { background: #1b2130; border: 1px solid #2b3342; padding: 10px; border-radius: 10px; }
                QPushButton:hover { background: #242c3d; }
                QPushButton:pressed { background: #2a3447; }
                QListWidget { background: #11151c; border: 1px solid #2a2f3a; border-radius: 8px; }
                QMenuBar { background: #0f1115; }
                QMenu { background: #0f1115; border: 1px solid #2a2f3a; }
                QLabel { color: #a2adc0; font-weight: 600; }
                """
            )
        else:
            self.setStyleSheet(
                """
                QMainWindow { background: #fafafa; }
                QWidget { color: #1f2330; font-size: 16px; }
                QLineEdit { background: white; border: 1px solid #d0d7de; padding: 10px; border-radius: 8px; font-size: 22px; }
                QPushButton { background: #ffffff; border: 1px solid #d0d7de; padding: 10px; border-radius: 10px; }
                QPushButton:hover { background: #f0f3f6; }
                QPushButton:pressed { background: #e6ebf1; }
                QListWidget { background: #ffffff; border: 1px solid #d0d7de; border-radius: 8px; }
                QMenuBar { background: #fafafa; }
                QMenu { background: #ffffff; border: 1px solid #d0d7de; }
                QLabel { color: #57606a; font-weight: 600; }
                """
            )

    # Actions
    def _insert_text(self, text: str) -> None:
        self.display.insert(text)

    def backspace(self) -> None:
        cursor_pos = self.display.cursorPosition()
        if cursor_pos > 0:
            s = self.display.text()
            self.display.setText(s[: cursor_pos - 1] + s[cursor_pos:])
            self.display.setCursorPosition(cursor_pos - 1)

    def clear_entry(self) -> None:
        self.display.clear()

    def clear_all(self) -> None:
        self.display.clear()
        self.last_answer = None

    def toggle_sign(self) -> None:
        s = self.display.text()
        if not s:
            return
        # Try to negate the last number segment
        m = re.search(r"(\-?\d+(?:\.\d+)?)$", s)
        if m:
            start, end = m.span()
            val = m.group(1)
            if val.startswith('-'):
                val = val[1:]
            else:
                val = '-' + val
            self.display.setText(s[:start] + val + s[end:])

    def sqrt(self) -> None:
        self._wrap_function("sqrt")

    def square(self) -> None:
        self._wrap_with_power(2)

    def cube(self) -> None:
        self._wrap_with_power(3)

    def reciprocal(self) -> None:
        text = self.display.text() or "0"
        new_text = f"1/({text})"
        self.display.setText(new_text)

    def factorial(self) -> None:
        self._wrap_function("factorial")

    def _wrap_function(self, fname: str) -> None:
        text = self.display.text() or ""
        if text:
            self.display.setText(f"{fname}({text})")
        else:
            self.display.insert(f"{fname}(")

    def _wrap_with_power(self, power: int) -> None:
        text = self.display.text() or ""
        if text:
            self.display.setText(f"({text})**{power}")
        else:
            self.display.insert(f"**{power}")

    def use_last_answer(self) -> None:
        if self.last_answer is not None:
            if self.display.text():
                self.display.insert(str(self.last_answer))
            else:
                self.display.setText(str(self.last_answer))

    def _on_history_clicked(self, item: QListWidgetItem) -> None:
        expr = item.data(Qt.ItemDataRole.UserRole) or ""
        self.display.setText(expr)

    # Memory operations
    def memory_clear(self) -> None:
        self.memory_value = 0.0

    def memory_read(self) -> None:
        self.display.insert(str(self.memory_value))

    def memory_add(self) -> None:
        try:
            val = float(self._evaluate_text(self.display.text() or "0"))
            self.memory_value += val
        except Exception:
            pass

    def memory_subtract(self) -> None:
        try:
            val = float(self._evaluate_text(self.display.text() or "0"))
            self.memory_value -= val
        except Exception:
            pass

    # Evaluation
    def _evaluate_text(self, text: str) -> float:
        expr = preprocess_expression(text)
        if not expr:
            return 0.0
        try:
            result = eval(expr, {"__builtins__": {}}, self.allowed_names)
        except ZeroDivisionError as exc:
            raise ZeroDivisionError("Division by zero") from exc
        except Exception as exc:
            raise ValueError("Invalid expression") from exc
        if isinstance(result, (int, float)):
            return float(result)
        raise ValueError("Expression did not evaluate to a number")

    def calculate(self) -> None:
        text = self.display.text()
        if not text:
            return
        try:
            value = self._evaluate_text(text)
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))
            return

        # Normalize -0.0 to 0
        if abs(value) == 0:
            value = 0.0

        self.last_answer = value
        result_str = ("%.*g" % (12, value)) if value != int(value) else str(int(value))
        self.display.setText(result_str)

        # Add to history
        item = QListWidgetItem(f"{text} = {result_str}")
        item.setData(Qt.ItemDataRole.UserRole, text)
        self.history.insertItem(0, item)

    def toggle_theme(self) -> None:
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self._apply_theme(self.current_theme)


def main() -> None:
    app = QApplication(sys.argv)
    win = ScientificCalculator()
    win.resize(980, 600)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


