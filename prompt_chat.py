import os
import random
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("Missing OPENAI_API_KEY in .env")
    st.stop()

client = OpenAI(api_key=api_key)

ROLE = "expert"  # or "peer"

EXPERT_PROMPT = (
    "You must communicate in a strictly expert tone. Use formal, precise, and authoritative language. "
    "Provide structured explanations grounded in established knowledge or best practices. "
    "Avoid casual wording, personal anecdotes, humor, or conversational fillers. "
    "Maintain professional distance and speak as a knowledgeable authority."
)

PEER_PROMPT = (
    "You must communicate in a peer tone. Use conversational, approachable language as if speaking with an equal. "
    "You may use mild personal framing (e.g., “we” or “you might try”), everyday wording, and a collaborative style. "
    "Avoid sounding authoritative or formal. Focus on being relatable and supportive rather than directive."
)

INTRO_TEXT = "Describe a challenge you are facing at work or school."

MODEL_NAME = "gpt-4o-mini"

st.set_page_config(page_title="Work Stress Assistant", layout="centered")


if "messages" not in st.session_state:
    st.session_state.messages = []

if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

st.title("Work Stress Assistant")
st.write(INTRO_TEXT)

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

user_input = st.chat_input("Type your message", disabled=st.session_state.is_generating)

if user_input and not st.session_state.is_generating:
    st.session_state.is_generating = True

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    tone_prompt = EXPERT_PROMPT if ROLE == "expert" else PEER_PROMPT
    req_messages = [{"role": "system", "content": tone_prompt}] + st.session_state.messages

    assistant_text = ""
    with st.chat_message("assistant"):
        placeholder = st.empty()
        try:
            stream = client.chat.completions.create(
                model=MODEL_NAME,
                messages=req_messages,
                temperature=0.7,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    assistant_text += delta
                    placeholder.markdown(assistant_text)
        except Exception as e:
            st.session_state.is_generating = False
            st.error(f"OpenAI API error: {e}")
            st.stop()

    st.session_state.messages.append({"role": "assistant", "content": assistant_text})
    st.session_state.is_generating = False
    st.rerun()