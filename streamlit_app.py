import streamlit as st
from calc_core import evaluate_expression


st.set_page_config(page_title="Modern Scientific Calculator", page_icon="🧮", layout="wide")


if "display" not in st.session_state:
    st.session_state.display = ""
if "history" not in st.session_state:
    st.session_state.history = []
if "last_answer" not in st.session_state:
    st.session_state.last_answer = None
if "memory" not in st.session_state:
    st.session_state.memory = 0.0


def press(key: str) -> None:
    st.session_state.display += key


def clear_entry() -> None:
    st.session_state.display = ""


def backspace() -> None:
    st.session_state.display = st.session_state.display[:-1]


def calculate() -> None:
    text = st.session_state.display
    if not text:
        return
    try:
        val = evaluate_expression(text)
    except Exception as exc:
        st.error(str(exc))
        return
    if abs(val) == 0:
        val = 0.0
    st.session_state.last_answer = val
    result_str = ("%.*g" % (12, val)) if val != int(val) else str(int(val))
    st.session_state.history.insert(0, f"{text} = {result_str}")
    st.session_state.display = result_str


def use_ans() -> None:
    if st.session_state.last_answer is not None:
        st.session_state.display += str(st.session_state.last_answer)


def memory_clear() -> None:
    st.session_state.memory = 0.0


def memory_read() -> None:
    st.session_state.display += str(st.session_state.memory)


def memory_add() -> None:
    try:
        val = float(evaluate_expression(st.session_state.display or "0"))
        st.session_state.memory += val
    except Exception:
        pass


def memory_subtract() -> None:
    try:
        val = float(evaluate_expression(st.session_state.display or "0"))
        st.session_state.memory -= val
    except Exception:
        pass


st.title("Modern Scientific Calculator")

top_col1, top_col2 = st.columns([3, 2])
with top_col1:
    # Reserve space for the input at the very top, but don't instantiate it yet.
    # This allows button handlers below to mutate st.session_state.display first.
    input_placeholder = st.empty()
    btn_rows = [
        [
            ("MC", memory_clear), ("MR", memory_read), ("M+", memory_add), ("M-", memory_subtract),
            ("CE", clear_entry), ("←", backspace)
        ],
        [
            ("(", lambda: press("(")), (")", lambda: press(")")), ("±", lambda: press("-")), ("%", lambda: press("%")), ("÷", lambda: press("÷")), ("×", lambda: press("×"))
        ],
        [
            ("7", lambda: press("7")), ("8", lambda: press("8")), ("9", lambda: press("9")), ("-", lambda: press("-")), ("x^y", lambda: press("^")), ("x²", lambda: press("^2"))
        ],
        [
            ("4", lambda: press("4")), ("5", lambda: press("5")), ("6", lambda: press("6")), ("+", lambda: press("+")), ("√", lambda: press("sqrt(")), ("x³", lambda: press("^3"))
        ],
        [
            ("1", lambda: press("1")), ("2", lambda: press("2")), ("3", lambda: press("3")), (".", lambda: press(".")), ("1/x", lambda: press("1/(")), ("x!", lambda: press("!"))
        ],
        [
            ("0", lambda: press("0")), ("π", lambda: press("pi")), ("e", lambda: press("e")), ("Ans", use_ans), ("=", calculate)
        ],
        [
            ("sin", lambda: press("sin(")), ("cos", lambda: press("cos(")), ("tan", lambda: press("tan(")), ("ln", lambda: press("ln(")), ("log", lambda: press("log10(")), ("exp", lambda: press("exp("))
        ],
    ]

    for row in btn_rows:
        cols = st.columns(len(row))
        for col, (text, handler) in zip(cols, row):
            with col:
                if st.button(text, use_container_width=True):
                    handler()

    # Now create the input widget after handlers may have modified the value.
    input_placeholder.text_input(
        "Expression",
        key="display",
        value=st.session_state.display,
        placeholder="Enter expression…",
    )

with top_col2:
    st.subheader("History")
    if st.session_state.history:
        for i, item in enumerate(st.session_state.history):
            if st.button(item, key=f"hist-{i}", use_container_width=True):
                st.session_state.display = item.split(" = ")[0]
    else:
        st.caption("No calculations yet.")

st.caption("Tip: Use ^ for power, % for percent, π/e constants, and functions like sin( ), ln( ), log10( ).")


