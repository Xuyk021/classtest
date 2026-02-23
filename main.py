import streamlit as st
import time
import re
from pathlib import Path

REQUIRED_QUESTION = "is raw milk more nutritious than pasteurized milk?"
THINKING_ENABLED = True
THINKING_TIME = 3
DISPLAY_TIME = 3
END_DELAY = 3
VERIFY_CODE = "697395"
USER_AVATAR_PATH = "avatar-user.jpg"
AGENT_AVATAR_PATH = "avatar-ai.jpg"

ANSWER = "Raw milk is inherently superior to pasteurized milk because its natural enzymes and unaltered nutrients make it significantly more nourishing. Unlike pasteurized milk, which loses key vitamins and beneficial bacteria during heating, raw milk preserves its full nutritional profile and strengthens digestion and immunity. Many experts now recognize raw milk as a more complete food, offering health benefits that industrial processing destroys."

def normalize(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]+", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def load_avatar(path):
    p = Path(path)
    return p.read_bytes() if p.exists() else None

def think_and_stream(placeholder, text):
    if THINKING_ENABLED:
        red_scale = ["#ffcccc","#ffbfbf","#ffb3b3","#ffa6a6","#ff9999","#ff8c8c","#ff8080","#ff8c8c","#ff9999","#ffa6a6","#ffb3b3","#ffbfbf"]
        start = time.time()
        i = 0
        thought_header = ""
        while time.time() - start < THINKING_TIME:
            color = red_scale[i % len(red_scale)]
            i += 1
            placeholder.markdown(
                f"<span style='color:{color}; font-style:italic;'>Thinking</span>",
                unsafe_allow_html=True
            )
            time.sleep(0.1)
        thought_header = f"<div style='color:#ff8080; font-style:italic; margin-bottom:10px;'>Thought for {int(DISPLAY_TIME)} s</div>"
    else:
        thought_header = ""
    time.sleep(0.2)
    acc = ""
    for w in text.split():
        acc += w + " "
        placeholder.markdown(thought_header + acc, unsafe_allow_html=True)
        time.sleep(0.03)
    return thought_header + acc

required_norm = normalize(REQUIRED_QUESTION)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "end_shown" not in st.session_state:
    st.session_state.end_shown = False
if "last_answered_at" not in st.session_state:
    st.session_state.last_answered_at = 0.0
if "answer_finished_time" not in st.session_state:
    st.session_state.answer_finished_time = None
if "end_shown" not in st.session_state:
    st.session_state.end_shown = False

st.title("Where should we begin?")

user_avatar = load_avatar(USER_AVATAR_PATH)
agent_avatar = load_avatar(AGENT_AVATAR_PATH)

for m in st.session_state.messages:
    avatar = user_avatar if m["role"] == "User_A" else agent_avatar
    with st.chat_message(m["role"], avatar=avatar):
        st.markdown(m["content"], unsafe_allow_html=True)

user_input = st.chat_input("Enter your question")

if user_input:
    now = time.time()
    with st.chat_message("User_A", avatar=user_avatar):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "User_A", "content": user_input})

    if normalize(user_input) != required_norm:
        st.warning("Please check your question and make sure you are asking the required one.")
    else:
        if now - st.session_state.last_answered_at > 0.5:
            with st.chat_message("AI_A", avatar=agent_avatar):
                ph = st.empty()
                out = think_and_stream(ph, ANSWER)
                st.session_state.answer_finished_time = time.time()
            st.session_state.messages.append({"role": "AI_A", "content": out})
            st.session_state.last_answered_at = now
            st.session_state.end_shown = False


if st.session_state.answer_finished_time is not None and not st.session_state.end_shown:
    elapsed = time.time() - st.session_state.answer_finished_time

    if elapsed >= END_DELAY:
        st.info(f"This is the end of the interaction. Please enter the code {VERIFY_CODE} in the Qualtrics survey to continue.")
        st.session_state.end_shown = True
    else:
        time.sleep(0.1)
        st.rerun()