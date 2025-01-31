import os
import json
import uuid
import streamlit as st
import torch
from transformers import pipeline

# Streamlit page configuration
st.set_page_config(page_title="Flagence Chat", page_icon="Flagence Chat", layout="wide")

# Load Hugging Face API key
working_dir = os.path.dirname(os.path.abspath(__file__))
try:
    config_data = json.load(open(f"{working_dir}/config.json"))
    HUGGINGFACE_API_KEY = config_data["HUGGINGFACE_API_KEY"]
except (FileNotFoundError, KeyError):
    st.error("HUGGINGFACE_API_KEY not found in config.json. Please add it.")
    st.stop()

# Model Selection (DeepSeek Coder - Choose a specific version)
model_name = "deepseek-ai/deepseek-coder-33b-instruct"  # Example: DeepSeek Coder 33B Instruct. Adjust as needed.
# Other DeepSeek Coder Models (check Hugging Face Hub for latest and sizes):
# "deepseek-ai/deepseek-coder-1.3b-base"
# "deepseek-ai/deepseek-coder-7b-instruct"
# "deepseek-ai/deepseek-coder-33b-instruct"  # Often a good balance
# "deepseek-ai/deepseek-coder-65b-instruct" # Large model, requires substantial resources

# Pipeline Creation (with memory management)
try:
    pipe = pipeline("text-generation", model=model_name, token=HUGGINGFACE_API_KEY, device_map="auto", load_in_8bit=True, trust_remote_code=True)  # Try 8-bit quantization first
except Exception as e:
    try:
        pipe = pipeline("text-generation", model=model_name, token=HUGGINGFACE_API_KEY, device_map="auto", trust_remote_code=True, torch_dtype=torch.float16) # Try float16 precision
        st.warning(f"Using float16 precision. Memory usage might be high. Error: {e}")
    except Exception as e:
        try:
            pipe = pipeline("text-generation", model=model_name, token=HUGGINGFACE_API_KEY, device_map="auto", trust_remote_code=True)  # Try without quantization (if you have enough resources)
            st.warning(f"No quantization applied. Memory usage might be very high. Error: {e}")
        except Exception as e:
            st.error(f"Model loading failed. Consider a smaller model or more resources. Error: {e}")
            st.stop()


# Initialize session states
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = []
if "current_chat" not in st.session_state:
    st.session_state.current_chat = []
if "user_key" not in st.session_state:
    st.session_state.user_key = str(uuid.uuid4())

# Sidebar for chat history
with st.sidebar:
    st.markdown("<h2 style='color:#333;'>Chat History</h2>", unsafe_allow_html=True)
    for idx, chat in enumerate(st.session_state.chat_histories):
        title = chat[0]["content"][:20] if chat else "New Chat"
        if st.button(f"Chat {idx + 1}: {title}"):
            st.session_state.current_chat = chat
    if st.button("New Chat"):
        if st.session_state.current_chat:
            st.session_state.chat_histories.append(st.session_state.current_chat)
        st.session_state.current_chat = []

# Main Page Layout (split for code)
col1, col2 = st.columns([1, 2])

with col1:  # Chat Area
    st.title("Flagence by FLAMEXD")
    chat_display = st.container()
    with chat_display:
        if st.session_state.current_chat:
            for message in st.session_state.current_chat:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    user_prompt = st.chat_input("Ask Flagence...")
    if user_prompt:
        st.chat_message("user").markdown(user_prompt)
        st.session_state.current_chat.append({"role": "user", "content": user_prompt})

        prompt = f"""
        You are a highly powerful coding assistant named Flagence by FLAMEXD. You are an expert in multiple programming languages. You can generate, explain, and debug code. Be concise and efficient in your responses.

        Current Conversation:
        """
        for message in st.session_state.current_chat:
            prompt += f"{message['role']}: {message['content']}\n"

        prompt += "assistant:"

        output = pipe(prompt,
                     max_new_tokens=512,
                     temperature=0.6,
                     top_p=0.9,
                     max_time=30
                     )
        assistant_response = output[0]["generated_text"].split("assistant:")[-1].strip()

        st.session_state.current_chat.append({"role": "assistant", "content": assistant_response})
        with st.chat_message("assistant"):
            st.markdown(assistant_response)

with col2:  # Code Area
    st.subheader("Code Output")
    if st.session_state.current_chat:
        for message in st.session_state.current_chat:
            if message["role"] == "assistant":
                code_blocks = message["content"].split("```")
                for i in range(1, len(code_blocks), 2):
                    try:
                        lang = code_blocks[i].split("\n")[0].strip()
                        code = "\n".join(code_blocks[i].split("\n")[1:]).strip()
                        st.code(code, language=lang)
                    except IndexError:
                        pass


# Styling (same as before)
st.markdown("""
    <style>
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
            padding-top: 20px;
        }
        .css-1lcbmhc { /* Sidebar title color */
            color: #333 !important;
        }
        .css-1y4p8pa { /* Sidebar buttons style */
            background-color: #007bff !important;
            color: #fff !important;
        }
        .css-1x8cf1d { /* Main title text color */
            color: #444 !important;
        }
    </style>
""", unsafe_allow_html=True)
