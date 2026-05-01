import streamlit as st
from google import genai
import matplotlib.pyplot as plt
from streamlit_mic_recorder import mic_recorder
from google.genai import types 

# --- 1. GRAPH FUNCTIONS ---
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
st.set_page_config(page_title="Bhagavanth AI", layout="centered", initial_sidebar_state="expanded")
st.title("🤖Bhagavanth AI Assistant")

if "client" not in st.session_state:
    # Replace with your actual API Key
    st.session_state.client = genai.Client(api_key=st.secrets["Google-API-Key"])
    st.session_state.chat_session = st.session_state.client.chats.create(model="gemini-3-flash")
    st.session_state.messages = []

# --- 3. SIDEBAR NAVIGATION MENU ---
with st.sidebar:
    st.header("🛠️ Main Menu")
    # This acts as your toggle menu
    menu_selection = st.selectbox("Select Panel", ["📈 Graph Data Panel", "📜 Chat History"])
    st.write("---")

    if menu_selection == "📈 Graph Data Panel":
        with st.form("graph_form"):
            st.subheader("Graph Input")
            input_labels = st.text_input("Labels", placeholder="e.g. Mon, Tue, Wed")
            input_values = st.text_input("Values", placeholder="e.g. 10, 20, 30")
            graph_title = st.text_input("Title", placeholder="e.g. Weekly Sales")
            graph_type = st.selectbox("Type", ["Line Chart", "Vertical Bar", "Horizontal Bar"])
            submitted = st.form_submit_button("Generate Graph")
    
    elif menu_selection == "📜 Chat History":
        st.subheader("Recent Conversation")
        if not st.session_state.messages:
            st.info("No history yet.")
        for msg in st.session_state.messages:
            role_icon = "👤" if msg["role"] == "user" else "🤖"
            # Show a snippet of the history in the sidebar
            st.write(f"{role_icon} **{msg['role'].capitalize()}**: {msg['content'][:50]}...")

# --- 4. MAIN CHAT DISPLAY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. GRAPH GENERATION LOGIC ---
if menu_selection == "📈 Graph Data Panel" and submitted:
    if not input_labels or not input_values:
        st.error("Please enter data to generate the graph.")
    else:
        labels = [i.strip() for i in input_labels.split(",") if i.strip()]
        try:
            values = [float(i.strip()) for i in input_values.split(",") if i.strip()]
            if len(labels) == len(values) > 0:
                st.write(f"### {graph_title or 'Visualization'}")
                if graph_type == "Line Chart": line(labels, values, "Items", "Values", graph_title)
                elif graph_type == "Vertical Bar": barsx(labels, values, "Values", graph_title)
                else: barsy(labels, values, "Values", graph_title)
            else: st.error("⚠️ Label count must match Value count!")
        except ValueError: st.error("⚠️ Values must be numbers!")

# --- 6. MULTIMODAL INPUT LOGOS (ATTACHMENTS) ---
st.write("---")
# Positioning the logos right above the text input
tool_col1, tool_col2, _ = st.columns([0.1, 0.4, 0.5])

with tool_col1:
    audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='recorder')

with tool_col2:
    uploaded_files = st.file_uploader(
        "Upload Files", 
        type=["png", "jpg", "jpeg", "pdf", "txt"], 
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

prompt = st.chat_input("Ask here...")
# --- 7. PROCESSING THE INPUT ---
audio_prompt = audio['bytes'] if audio else None

# Initialize variables to avoid NameErrors
user_parts = []
display_text = "" 

if prompt or audio_prompt or uploaded_files:
    # 1. Handle Text
    if prompt:
        user_parts.append(types.Part.from_text(text=prompt))
        display_text += prompt
    
    # 2. Handle Audio
    if audio_prompt:
        user_parts.append(types.Part.from_bytes(data=audio_prompt, mime_type="audio/wav"))
        display_text += " 🎤 _[Voice Command]_ "

    # 3. Handle Files (Images, PDFs, etc.)
    if uploaded_files:
        for f in uploaded_files:
            # Use from_bytes to wrap the file data correctly
            user_parts.append(types.Part.from_bytes(data=f.getvalue(), mime_type=f.type))
        display_text += f" 📎 _[{len(uploaded_files)} Attachment(s)]_"

    # Save to session state for the UI
    st.session_state.messages.append({"role": "user", "content": display_text})
    
    with st.chat_message("user"):
        st.markdown(display_text)

    try:
        # Send the list of Part objects to the model
        response = st.session_state.chat_session.send_message(user_parts)
        
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        with st.chat_message("assistant"):
            st.markdown(response.text)
    except Exception as e:
        st.error(f"AI Connection Error: {e}")

