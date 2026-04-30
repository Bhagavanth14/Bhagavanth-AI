import streamlit as st
from google import genai

# --- 1. SET UP THE PAGE ---
st.set_page_config(page_title="My AI Assistant", layout="centered")
st.title("🤖 Bhagavanth AI Assistant")

# --- 2. INITIALIZE AI CLIENT & CHAT ---
# We use 'session_state' so the AI memory doesn't reset on every click
if "chat_session" not in st.session_state:
    client = genai.Client(api_key=st.secrets["AIzaSyA2maYnZeZ9dlr0A0vrdxUDnrwkvLkXtpU"])
    # This replaces your 'chat = client.chats.create' line
    st.session_state.chat_session = client.chats.create(model="gemini-2.5-flash")
    # This stores the visible message history for the UI
    st.session_state.messages = []

# --- 3. DISPLAY MESSAGE HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. HANDLE USER INPUT ---
if prompt := st.chat_input("ASK HERE:"):
    # Show user message in the app
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Send message to the AI (using the session we saved)
    try:
        response = st.session_state.chat_session.send_message(prompt)
        
        # Show AI response in the app
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"An error occurred: {e}")
