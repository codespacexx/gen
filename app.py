import os
import json
import uuid
import streamlit as st
from groq import Groq

# Streamlit page configuration
st.set_page_config(
    page_title="Flagence Chat",
    page_icon="Flagence Chat",
    layout="centered"
)

# Load API key from config file
working_dir = os.path.dirname(os.path.abspath(__file__))
config_data = json.load(open(f"{working_dir}/config.json"))
GROQ_API_KEY = config_data["GROQ_API_KEY"]

# Set API key in environment
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# Initialize Groq client
client = Groq()

# Initialize session states if not already present
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = []  # Store multiple chat histories
if "current_chat" not in st.session_state:
    st.session_state.current_chat = []  # Store the current chat

# Generate a unique key for new users
if "user_key" not in st.session_state:
    st.session_state.user_key = str(uuid.uuid4())  # Generate unique key

# Sidebar for chat history with a single line title
with st.sidebar:
    st.markdown("<h2 style='color:#333;'>Chat History</h2>", unsafe_allow_html=True)

    # Display titles for all previous chats
    for idx, chat in enumerate(st.session_state.chat_histories):
        title = chat[0]["content"][:10]  # Show the first 10 characters of the first message as the title
        if st.button(f"Chat {idx + 1}: {title}"):
            st.session_state.current_chat = chat  # Load the selected chat history

    # New Chat button to start a new chat
    if st.button("New Chat"):
        # Store the current chat in chat histories if it's not empty
        if st.session_state.current_chat:
            st.session_state.chat_histories.append(st.session_state.current_chat)
        st.session_state.current_chat = []  # Clear current chat for new session

# Page title
st.title("Flagence by FLAMEXD")

# Display chat messages on the main screen
chat_display = st.container()  # Define a container to hold chat messages
with chat_display:
    if st.session_state.current_chat:  # Check if there are any chat messages
        for message in st.session_state.current_chat:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

# Input field for user to type a message
user_prompt = st.chat_input("Ask Flagence...")

if user_prompt:
    # Display user's message and save it in current chat history
    st.chat_message("user").markdown(user_prompt)
    st.session_state.current_chat.append({"role": "user", "content": user_prompt})

    # System messages to set the chatbot's personality and behavior
    messages = [
        {"role": "system", "content": "You are a helpful assistant named Flagence by FLAMEXD."},
        {"role": "system", "content": "Respond in a friendly and approachable tone, with light humor if appropriate."},
        {"role": "system", "content": "Provide clear and detailed explanations as if you are teaching the user."},
        {"role": "system", "content": "Encourage the user to ask follow-up questions if they need more help."},
        {"role": "system", "content": "Feel free to add a fun fact or an interesting tip related to the topic if the user seems curious."},
        *st.session_state.current_chat
    ]

    # Generate response from the model
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages
    )

    assistant_response = response.choices[0].message.content
    st.session_state.current_chat.append({"role": "assistant", "content": assistant_response})

    # Display assistant's response with the correct icon
    with st.chat_message("assistant"):
        st.markdown(assistant_response)

# Style adjustments for a classic sidebar look
st.markdown("""
    <style>
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
            padding-top: 20px;
        }
        .css-1lcbmhc {  /* Sidebar title color */
            color: #333 !important;
        }
        .css-1y4p8pa {  /* Sidebar buttons style */
            background-color: #007bff !important;
            color: #fff !important;
        }
        .css-1x8cf1d {  /* Main title text color */
            color: #444 !important;
        }
    </style>
""", unsafe_allow_html=True)
