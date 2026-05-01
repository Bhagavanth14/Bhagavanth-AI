import streamlit as st
from google import genai
import matplotlib.pyplot as plt

# --- 1. YOUR GRAPH FUNCTIONS ---
def line(x, y, xlab, ylab, tit):
    fig, ax = plt.subplots()
    ax.plot(x, y, marker='o', color='b')
    ax.set_title(tit)
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    st.pyplot(fig)

def barsx(x, y, ylab, tit):
    fig, ax = plt.subplots()
    ax.bar(x, y, color='skyblue')
    ax.set_ylabel(ylab)
    ax.set_title(tit)
    st.pyplot(fig)

def barsy(x, y, xlab, tit):
    fig, ax = plt.subplots()
    ax.barh(x, y, color='salmon')
    ax.set_xlabel(xlab)
    ax.set_title(tit)
    st.pyplot(fig)

# --- 2. APP SETUP ---
st.set_page_config(page_title="Bhagavanth AI", layout="centered")
st.title("🤖Bhagavanth AI Assistant & Custom Grapher")

if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key="YOUR_API_KEY")
    st.session_state.chat_session = st.session_state.client.chats.create(model="gemini-2.0-flash")
    st.session_state.messages = []

# --- 3. SIDEBAR FOR DATA INPUT ---
with st.sidebar:
    st.header("📈 Graph Data Input")
    st.write("Enter labels and values separated by commas.")
    
    input_labels = st.text_input("Labels (e.g. LED, Bulb, Tube)", "A, B, C")
    input_values = st.text_input("Values (e.g. 10, 20, 30)", "10, 20, 30")
    
    graph_title = st.text_input("Graph Title", "My Analysis")
    
    # Process the strings into lists
    labels_list = [i.strip() for i in input_labels.split(",")]
    try:
        values_list = [float(i.strip()) for i in input_values.split(",")]
    except ValueError:
        st.error("Please enter numbers only in the Values box.")
        values_list = [0]

# --- 4. UI DISPLAY (CHAT HISTORY) ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. CHAT INPUT & BUTTONS ---
prompt = st.chat_input("Ask the AI something...")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📈 Line Chart"):
        line(labels_list, values_list, "Items", "Count", graph_title)

with col2:
    if st.button("📊 Vertical Bar"):
        barsx(labels_list, values_list, "Count", graph_title)

with col3:
    if st.button("↔️ Horizontal Bar"):
        barsy(labels_list, values_list, "Count", graph_title)

# --- 6. AI LOGIC ---
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        response = st.session_state.chat_session.send_message(prompt)
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Error: {e}")
