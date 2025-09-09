# Calculator
Calculator built by Basant
Modern Scientific Calculator (PyQt6)
====================================

An elegant, modern-looking scientific calculator built with PyQt6. It supports common and advanced operations, has a clean dark/light theme, keyboard shortcuts, memory keys, and a clickable history.

Features
--------
- Clean, modern UI with dark and light themes (toggle with Ctrl+T)
- Real-time expression entry with keyboard and on-screen buttons
- Advanced functions: sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, ln, log10, exp, sqrt, x², x³, x^y, 1/x, factorial, degrees, radians
- Constants: π (`pi`), e (`e`), τ (`tau`)
- Operators: +, −, ×, ÷, ^ (power), parentheses, percent `%` converts to `/100`
- Memory keys: MC, MR, M+, M−
- History panel: click an entry to reuse the expression
- Ans button to reuse the last result
- Safe evaluation sandbox: only math functions/constants are allowed

Install
-------
1. Ensure Python 3.9+ is installed.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

Run
---

```bash
python calculator.py
```

Usage tips
----------
- Use `^` for exponentiation (e.g., `2^8`), `%` will be interpreted as `/100` for numbers (e.g., `12%` → `0.12`).
- Factorial accepts styles like `5!`, `(3+2)!`, and even `5!!`.
- Use `ln(` for natural log, `log(` inserts base-10 log, `exp(` for e^x.
- Insert constants with `π` or `e` buttons.
- Press Enter to calculate, Esc to clear entry, Backspace to delete.

Notes
-----
- Expressions are evaluated with Python’s math library (e.g., `sin` expects radians; use `degrees` / `radians` to convert).
- Division by zero and invalid expressions are caught and shown as error dialogs.

License
-------
MIT