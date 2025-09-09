import streamlit as st
from calc_core import evaluate_expression


st.set_page_config(page_title="Modern Scientific Calculator", page_icon="🧮", layout="wide")

# Subtle, colorful styling
st.markdown(
    """
    <style>
    .app-title h1 { 
        background: linear-gradient(90deg, #7c3aed, #2563eb, #10b981);
        -webkit-background-clip: text; background-clip: text; color: transparent; 
        font-weight: 800; letter-spacing: -0.5px;
    }
    .stButton > button {
        background: linear-gradient(180deg, #ffffff, #f3f4f6);
        border: 1px solid #e5e7eb; color: #111827; border-radius: 12px; height: 46px;
        box-shadow: 0 1px 1px rgba(0,0,0,0.04), inset 0 -1px 0 rgba(0,0,0,0.02);
        transition: all .15s ease-in-out; font-weight: 600;
    }
    .stButton > button:hover { background: #eef2ff; border-color: #c7d2fe; }
    .stButton > button:active { transform: translateY(1px); }
    .primary-equals > button { background: linear-gradient(180deg, #34d399, #10b981); color: white; border: none; }
    .danger-clear > button { background: linear-gradient(180deg, #fca5a5, #f87171); color: white; border: none; }
    .accent-ops > button { background: linear-gradient(180deg, #c7d2fe, #a5b4fc); color: #111827; border: none; }
    .stTextInput > div > div > input { border-radius: 12px; border: 1px solid #e5e7eb; height: 48px; }
    </style>
    """,
    unsafe_allow_html=True,
)


if "display" not in st.session_state:
    st.session_state.display = ""
if "history" not in st.session_state:
    st.session_state.history = []
if "last_answer" not in st.session_state:
    st.session_state.last_answer = None
if "memory" not in st.session_state:
    st.session_state.memory = 0.0
if "advanced" not in st.session_state:
    st.session_state.advanced = False


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


st.markdown('<div class="app-title">\n<h1>Modern Scientific Calculator</h1>\n</div>', unsafe_allow_html=True)

top_col1, top_col2 = st.columns([3, 2])
with top_col1:
    # Reserve space for the input at the very top, but don't instantiate it yet.
    # This allows button handlers below to mutate st.session_state.display first.
    input_placeholder = st.empty()
    advanced = st.toggle("Advanced mode", value=st.session_state.advanced, help="Switch between basic and advanced functions")
    st.session_state.advanced = advanced

    # Define keypad buttons; include advanced rows conditionally
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
    ]

    if advanced:
        btn_rows.append([
            ("sin", lambda: press("sin(")), ("cos", lambda: press("cos(")), ("tan", lambda: press("tan(")), ("ln", lambda: press("ln(")), ("log", lambda: press("log10(")), ("exp", lambda: press("exp("))
        ])

    for row in btn_rows:
        cols = st.columns(len(row))
        for idx, (text, handler) in enumerate(row):
            col = cols[idx]
            with col:
                # Assign subtle styles to certain action groups
                btn_container = st.container()
                btn_class = ""
                if text in ("=",):
                    btn_class = "primary-equals"
                elif text in ("CE",):
                    btn_class = "danger-clear"
                elif text in ("+", "-", "×", "÷", "x^y", "x²", "x³", "√"):
                    btn_class = "accent-ops"
                with btn_container:
                    if st.button(text, use_container_width=True, key=f"btn-{text}-{idx}"):
                        handler()
                if btn_class:
                    st.markdown(f"<style>.element-container:has(> div button[data-testid='baseButton'][aria-label='{text}']) > div > button {{}} </style>", unsafe_allow_html=True)
                    # Fallback: apply class to last rendered button
                    st.markdown(f"<script>const bs=document.querySelectorAll('.stButton button'); if(bs.length) bs[bs.length-1].parentElement.classList.add('{btn_class}');</script>", unsafe_allow_html=True)

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


