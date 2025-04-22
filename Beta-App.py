import streamlit as st
import re
from collections import defaultdict
import random

# ---------- CONFIG ----------
st.set_page_config(page_title="Beta App", layout="centered")
st.title("Beta App")

# ---------- INIT STATES ----------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "number_history" not in st.session_state:
    st.session_state.number_history = defaultdict(int)
if "movement_log" not in st.session_state:
    st.session_state.movement_log = []
if "predictions" not in st.session_state:
    st.session_state.predictions = []
if "corrections_log" not in st.session_state:
    st.session_state.corrections_log = []
if "movement_input_learn" not in st.session_state:
    st.session_state.movement_input_learn = ""

# ---------- PASSCODE ----------
if not st.session_state.authenticated:
    code = st.text_input("Enter passcode to access:", type="password")
    if code == "2579":
        st.session_state.authenticated = True
        st.experimental_rerun()
    elif code != "":
        st.error("Incorrect passcode ❌")
    st.stop()

# ---------- RESET ----------
if st.button("🔁 Reset All Data"):
    st.session_state.number_history = defaultdict(int)
    st.session_state.movement_log = []
    st.session_state.predictions = []
    st.session_state.corrections_log = []
    st.session_state.movement_input_learn = ""
    st.success("All data reset.")

# ---------- NUMBER ENTRY ----------
st.subheader("Enter Numbers")

with st.form("number_input_form", clear_on_submit=True):
    user_input = st.text_input("Input numbers (e.g. 1 00 17 or 1, 00, 17):")
    submit_numbers = st.form_submit_button("Submit Numbers")

    def parse_input_numbers(text):
        numbers = re.split(r"[,\s]+", text.strip())
        valid_numbers = []
        for n in numbers:
            if n == "00":
                valid_numbers.append("00")
            elif n.isdigit() and 0 <= int(n) <= 36:
                valid_numbers.append(int(n))
        return valid_numbers

    if submit_numbers:
        entries = parse_input_numbers(user_input)
        if not entries:
            st.warning("No valid numbers entered.")
        else:
            for n in entries:
                st.session_state.number_history[n] += 1
            st.session_state.movement_log.append({"numbers": entries, "movement": None})
            st.success(f"Recorded: {entries}")

# ---------- BALL MOVEMENT ----------
st.subheader("Ball Movement")

with st.form("movement_only_form"):
    st.text_input("How many spaces did the ball move?", key="movement_input_learn")
    movement_submit = st.form_submit_button("Submit Ball Movement")

    if movement_submit:
        movement = st.session_state.get("movement_input_learn", "").strip()
        if movement.isdigit():
            st.session_state.movement_log.append({
                "numbers": [],
                "movement": int(movement)
            })
            st.success(f"Ball movement of {movement} recorded.")
        else:
            st.warning("Please enter a valid number (0 or more).")
        st.session_state.movement_input_learn = ""

# ---------- AI PREDICTION ----------
st.subheader("AI Prediction")

def predict_next_numbers():
    if not st.session_state.number_history:
        return random.sample(list(range(37)) + ["00"], 5)
    sorted_nums = sorted(st.session_state.number_history.items(), key=lambda x: x[1], reverse=True)
    return [n[0] for n in sorted_nums[:5]]

st.session_state.predictions = predict_next_numbers()
st.write("📈 Predicted Next Numbers: **" + ', '.join(str(n) for n in st.session_state.predictions) + "**")

# ---------- CORRECTION ----------
st.subheader("Correction")

with st.form("correction_form", clear_on_submit=True):
    correction_input = st.text_input("If prediction was wrong, enter the actual number(s):")
    correction_submit = st.form_submit_button("Submit Correction")

    if correction_submit:
        corrected = parse_input_numbers(correction_input)
        if corrected:
            for n in corrected:
                st.session_state.number_history[n] += 1
            st.session_state.corrections_log.append(corrected)
            st.success(f"Correction saved: {corrected}")
        else:
            st.warning("Please enter a valid number for correction.")

if st.session_state.corrections_log:
    st.subheader("Corrections Made")
    correction_table = []
    for i, c in enumerate(st.session_state.corrections_log, 1):
        correction_table.append({"Correction #": i, "Actual Numbers": ', '.join(str(n) for n in c)})
    st.table(correction_table)

# ---------- BALL HISTORY ----------
st.subheader("Ball History")

if st.session_state.movement_log:
    movement_table = []
    for i, entry in enumerate(st.session_state.movement_log, 1):
        movement_table.append({
            "Entry #": i,
            "Spaces Moved": entry["movement"] if entry["movement"] is not None else "—",
            "Numbers Entered": ', '.join(str(n) for n in entry["numbers"]) if entry["numbers"] else "—"
        })
    st.table(movement_table)
else:
    st.info("No movement data recorded yet.")

# ---------- NUMBER HISTORY ----------
st.subheader("Number History")

if st.session_state.number_history:
    history_table = [{"Number": str(k), "Times Seen": v} for k, v in sorted(st.session_state.number_history.items())]
    st.table(history_table)
else:
    st.info("No numbers submitted yet.")

# ---------- ROULETTE IMAGE AT BOTTOM ----------
st.markdown(
    """
    <div style="text-align: center; padding-top: 20px;">
        <a href="https://postimg.cc/R3JJZZTT" target="_blank">
            <img src="https://i.postimg.cc/R3JJZZTT/Wheel-png.webp"
                 style="max-width: 95%; height: auto; border: 1px solid #ccc;"
                 alt="Roulette Wheel">
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
