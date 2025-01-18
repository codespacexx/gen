import os
import json
import uuid
import streamlit as st
from groq import Groq
import datetime
import random

# Streamlit page configuration
st.set_page_config(
    page_title="ALVXD AI Chat",
    page_icon="ALVXD AI",
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
if "user_key" not in st.session_state:
    st.session_state.user_key = str(uuid.uuid4())  # Generate unique key

# User Greeting and Fun Fact
if "last_visited" not in st.session_state or (st.session_state.last_visited != str(datetime.date.today())):
    st.session_state.last_visited = str(datetime.date.today())
    st.chat_message("assistant").markdown("Hello, welcome to **ALVXD AI**! How can I assist you today?")

# Fun Fact Feature
fun_facts = [
    "Did you know? The first AI program was written in 1951 by Christopher Strachey, later director of the Programming Research Group at the University of Oxford.",
    "Fun fact: In 1956, John McCarthy coined the term ‘artificial intelligence’ during the famous Dartmouth Conference.",
    "Here’s a random fun fact: The word 'robot' comes from the Czech word 'robota,' which means forced labor."
]
if random.choice([True, False]):
    fun_fact = random.choice(fun_facts)
    st.chat_message("assistant").markdown(f"🤖 Fun Fact: {fun_fact}")

# Sidebar for chat history with a single line title
with st.sidebar:
    st.markdown("<h2 style='color:#333;'>Chat History</h2>", unsafe_allow_html=True)
    for idx, chat in enumerate(st.session_state.chat_histories):
        title = chat[0]["content"][:10]  # Show the first 10 characters of the first message as the title
        if st.button(f"Chat {idx + 1}: {title}"):
            st.session_state.current_chat = chat  # Load the selected chat history
    if st.button("New Chat"):
        if st.session_state.current_chat:
            st.session_state.chat_histories.append(st.session_state.current_chat)
        st.session_state.current_chat = []  # Clear current chat for new session

# Page title
st.title("ALVXD AI - Powered by Alvexd & Zannat")

# Display chat messages on the main screen
chat_display = st.container()
with chat_display:
    if st.session_state.current_chat:
        for message in st.session_state.current_chat:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

# Input field for user to type a message
user_prompt = st.chat_input("Ask ALVXD AI...")
if user_prompt:
    st.chat_message("user").markdown(user_prompt)
    st.session_state.current_chat.append({"role": "user", "content": user_prompt})

    # System messages to set the chatbot's personality and behavior
    messages = [
        {"role": "system", "content": "You are ALVXD AI, a helpful assistant created by Alvexd."},
        {"role": "system", "content": "Your assistant, Zannat, will assist you in delivering information with a warm and friendly tone."},
        {"role": "system", "content": "Respond with clear, friendly, and detailed explanations."},
        {"role": "system", "content": "Encourage the user to ask follow-up questions if they need more help."},
        {"role": "system", "content": "Add a fun fact or an interesting tip related to the topic when appropriate."},
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
        .stChatMessage p { /* User and assistant message colors */
            color: #333 !important;
        }
        .st-chat-message p.user {
            background-color: #e0f7fa !important;
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 10px;
        }
        .st-chat-message p.assistant {
            background-color: #f1f8e9 !important;
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)
