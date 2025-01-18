import os
import json
import uuid
import streamlit as st
from groq import Groq


def load_config():
    """Load configuration from config.json."""
    try:
        working_dir = os.path.dirname(os.path.abspath(__file__))
        with open(f"{working_dir}/config.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        st.error("Configuration file not found. Please ensure config.json exists.")
        st.stop()
    except json.JSONDecodeError:
        st.error("Error parsing config.json. Ensure it is correctly formatted.")
        st.stop()


def initialize_session_state():
    """Initialize session states for chat management."""
    if "chat_histories" not in st.session_state:
        st.session_state.chat_histories = []
    if "current_chat" not in st.session_state:
        st.session_state.current_chat = []
    if "user_key" not in st.session_state:
        st.session_state.user_key = str(uuid.uuid4())


def save_current_chat():
    """Save the current chat to chat histories if it's not empty."""
    if st.session_state.current_chat:
        st.session_state.chat_histories.append(st.session_state.current_chat)
    st.session_state.current_chat = []


def display_sidebar():
    """Render the sidebar with chat history navigation and user options."""
    with st.sidebar:
        st.markdown("<h2 style='color:#333;'>Chat History</h2>", unsafe_allow_html=True)

        # Display saved chat history
        for idx, chat in enumerate(st.session_state.chat_histories):
            if chat:  # Ensure non-empty chat histories
                title = chat[0]["content"][:20] + "..."  # Shortened title
                if st.button(f"Chat {idx + 1}: {title}", key=f"chat_{idx}"):
                    st.session_state.current_chat = chat

        # New chat button with styling
        if st.button("New Chat", key="new_chat"):
            save_current_chat()


def render_chat_interface(client):
    """Render the main chat interface with a more professional UI."""
    st.title("Flagence by FLAMEXD")
    st.markdown("<h5 style='color: #007bff;'>Your AI Assistant</h5>", unsafe_allow_html=True)

    # Styling for better separation and visual hierarchy
    chat_display = st.container()
    with chat_display:
        if st.session_state.current_chat:
            for message in st.session_state.current_chat:
                with st.chat_message(message["role"]):
                    if message["role"] == "user":
                        st.markdown(f"<div style='background-color:#e1f5fe; padding: 10px; border-radius: 8px;'>{message['content']}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div style='background-color:#f1f8e9; padding: 10px; border-radius: 8px;'>{message['content']}</div>", unsafe_allow_html=True)

    user_prompt = st.chat_input("Ask Flagence...", key="user_prompt")
    if user_prompt:
        process_user_message(user_prompt, client)


def process_user_message(user_prompt, client):
    """Process the user message and generate a chatbot response."""
    # Append user message to current chat
    st.session_state.current_chat.append({"role": "user", "content": user_prompt})
    st.chat_message("user").markdown(user_prompt)

    # System instructions for the assistant
    system_messages = [
        {"role": "system", "content": "You are a helpful assistant named Flagence by FLAMEXD."},
        {"role": "system", "content": "Respond in a friendly and approachable tone."},
        {"role": "system", "content": "Provide clear and detailed explanations with light humor."},
    ]

    # Build the message list
    messages = system_messages + st.session_state.current_chat

    # Generate a response from the model
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )
        assistant_response = response.choices[0].message.content
        st.session_state.current_chat.append({"role": "assistant", "content": assistant_response})
        with st.chat_message("assistant"):
            st.markdown(f"<div style='background-color:#f1f8e9; padding: 10px; border-radius: 8px;'>{assistant_response}</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error generating response: {e}")


def apply_custom_styles():
    """Apply custom styles for a polished and professional user experience."""
    st.markdown("""
        <style>
            .sidebar .sidebar-content {
                background-color: #f4f6f9;
                padding-top: 20px;
                border-right: 2px solid #dcdcdc;
            }
            .css-1lcbmhc {
                color: #333 !important;
                font-size: 18px;
                font-weight: bold;
            }
            .css-1y4p8pa {
                background-color: #007bff !important;
                color: #fff !important;
                border-radius: 5px;
                font-size: 16px;
                padding: 10px;
            }
            .css-1x8cf1d {
                color: #444 !important;
                font-size: 22px;
                margin-bottom: 10px;
            }
            .streamlit-expanderHeader {
                font-weight: bold;
                color: #007bff;
            }
            .streamlit-expanderContent {
                background-color: #f8f9fa;
            }
        </style>
    """, unsafe_allow_html=True)


def display_faq_section():
    """Render a FAQ section for user guidance."""
    with st.expander("FAQs", expanded=False):
        st.markdown("""
            <ul>
                <li><strong>How do I start a new chat?</strong> Click the 'New Chat' button on the sidebar.</li>
                <li><strong>What is Flagence?</strong> Flagence is an AI assistant built to help you with a variety of tasks.</li>
                <li><strong>Can I customize Flagence?</strong> Yes, we will soon support additional customization options!</li>
            </ul>
        """, unsafe_allow_html=True)


def main():
    """Main function to run the Streamlit app."""
    # Streamlit page configuration
    st.set_page_config(
        page_title="Flagence Chat",
        page_icon="Flagence Chat",
        layout="centered",
        initial_sidebar_state="expanded"
    )

    # Load configuration
    config_data = load_config()

    # Set API key in the environment
    os.environ["GROQ_API_KEY"] = config_data["GROQ_API_KEY"]

    # Initialize Groq client
    client = Groq()

    # Initialize session state variables
    initialize_session_state()

    # Display sidebar with chat history
    display_sidebar()

    # Render chat interface
    render_chat_interface(client)

    # Display FAQs and additional information
    display_faq_section()

    # Apply custom styles
    apply_custom_styles()


if __name__ == "__main__":
    main()
