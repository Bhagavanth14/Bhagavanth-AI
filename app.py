import streamlit as st
from google import genai
import matplotlib.pyplot as plt

# --- 1. YOUR GRAPH FUNCTIONS ---
def line(x, y, xlab, ylab, tit):
    fig, ax = plt.subplots()
    ax.plot(x, y, marker='o', color='b', linewidth=2)
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
st.title("🤖 AI Assistant & 📊Custom Grapher")

if "client" not in st.session_state:
    # Use your actual key here or st.secrets for deployment
    st.session_state.client = genai.Client(api_key=st.secrets[Google-API-Key])
    st.session_state.chat_session = st.session_state.client.chats.create(model="gemini-2.5-flash")
    st.session_state.messages = []

# --- 3. SIDEBAR INPUT FORM ---
with st.sidebar:
    st.header("📋 Graph Configuration")
    # Empty default values (None or "") 
    with st.form("graph_form"):
        input_labels = st.text_input("Enter Labels (comma separated)", value="", placeholder="e.g. LED, Strip, Bulb")
        input_values = st.text_input("Enter Values (comma separated)", value="", placeholder="e.g. 50, 120, 80")
        graph_title = st.text_input("Graph Title", value="", placeholder="e.g. May Sales Report")
        graph_type = st.selectbox("Choose Graph Type", ["Line Chart", "Vertical Bar", "Horizontal Bar"])
        
        submitted = st.form_submit_button("Generate Graph")

# --- 4. UI DISPLAY (CHAT HISTORY) ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. GRAPH LOGIC & SIDEBAR INDICATOR ---
if submitted:
    # Check if inputs are empty
    if not input_labels or not input_values:
        st.info("👈 **Please enter your data in the sidebar to visualize it.**")
        st.sidebar.warning("Fill these fields first!")
    else:
        labels = [i.strip() for i in input_labels.split(",") if i.strip()]
        try:
            values = [float(i.strip()) for i in input_values.split(",") if i.strip()]
            
            if len(labels) == len(values) and len(labels) > 0:
                st.write(f"### {graph_title if graph_title else 'Data Visualization'}")
                if graph_type == "Line Chart":
                    line(labels, values, "Items", "Values", graph_title)
                elif graph_type == "Vertical Bar":
                    barsx(labels, values, "Values", graph_title)
                else:
                    barsy(labels, values, "Values", graph_title)
            else:
                st.error("⚠️ The number of labels and values must match!")
        except ValueError:
            st.error("⚠️ Make sure the values are numbers separated by commas.")

# --- 6. AI CHAT INPUT ---
if prompt := st.chat_input("Ask me anything..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        response = st.session_state.chat_session.send_message(prompt)
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Chat Error: {e}")
