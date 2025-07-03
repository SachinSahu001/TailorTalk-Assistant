import os
from dotenv import load_dotenv # type: ignore
import streamlit as st # type: ignore
import requests # type: ignore

load_dotenv()


model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

st.set_page_config(page_title="TailorTalk Bot 🤖", page_icon="🧵")

st.title("🤖 TailorTalk Calendar Assistant")
st.markdown(f"Using Model: `{model_name}`")

# Store chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat display
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_input = st.chat_input("Type something...")

if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Send to backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                res = requests.post("https://tailortalk-backend-production.up.railway.app/chat", json={"message": user_input})
                if res.status_code == 200:
                    reply = res.json().get("response", "No response from bot.")
                else:
                    reply = f"❌ Backend error {res.status_code}: {res.text}"
            except requests.exceptions.RequestException as e:
                reply = f"❌ Could not connect to backend: {e}"
            except Exception as e:
                reply = f"❌ Unexpected error: {str(e)}"

        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
