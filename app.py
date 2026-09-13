import os
import streamlit as st
import requests
import json
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Local LLM Chat",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
    }
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 20px;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 2rem;
        border-bottom-right-radius: 5px;
    }
    .assistant-message {
        background: #f0f2f6;
        color: black;
        margin-right: 2rem;
        border-bottom-left-radius: 5px;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


# ── Ollama helpers ───────────────────────────────────────────────────────────
def get_ollama_host():
    """Return the Ollama base URL from secrets, env, or default.

    Safe to call even when no secrets.toml file exists.
    """
    try:
        host = st.secrets.get("OLLAMA_HOST", "")
        if host:
            return host
    except Exception:
        # No secrets.toml file, or key missing - fall through to env/default.
        pass
    return os.environ.get("OLLAMA_HOST", "http://localhost:11434")


def check_ollama(host):
    """Return True if Ollama is reachable."""
    try:
        r = requests.get(f"{host}/api/tags", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def list_models(host):
    """Fetch available models from Ollama."""
    try:
        r = requests.get(f"{host}/api/tags", timeout=10)
        r.raise_for_status()
        return r.json().get("models", [])
    except Exception:
        return []


def chat(host, model, messages, stream=True):
    """Call Ollama's chat API. Yields chunks when streaming."""
    payload = {
        "model": model,
        "messages": messages,
        "stream": stream,
        "options": {
            "temperature": st.session_state.get("temperature", 0.7),
            "top_p": st.session_state.get("top_p", 0.9),
            "num_predict": st.session_state.get("num_predict", 2048),
        },
    }
    with requests.post(
        f"{host}/api/chat",
        json=payload,
        stream=stream,
        timeout=120,
    ) as r:
        r.raise_for_status()
        if stream:
            for line in r.iter_lines(decode_unicode=True):
                if line:
                    yield json.loads(line)
        else:
            yield r.json()


# ── Session state init ───────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_id" not in st.session_state:
    st.session_state.chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7
if "top_p" not in st.session_state:
    st.session_state.top_p = 0.9
if "num_predict" not in st.session_state:
    st.session_state.num_predict = 2048


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Settings")

    host = st.text_input("Ollama Host", value=get_ollama_host(), key="host_input")

    online = check_ollama(host)
    if online:
        st.success("Ollama connected")
    else:
        st.error("Cannot reach Ollama")

    models = list_models(host) if online else []
    model_names = [m["name"] for m in models]

    if model_names:
        selected_model = st.selectbox("Model", model_names, index=0)
    else:
        selected_model = st.text_input("Model name", "llama3.2:3b", key="model_input")
        st.caption("Enter model name manually (e.g. llama3.2:3b, mistral, codellama)")

    st.divider()
    st.subheader("Generation")
    temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1, key="temp_slider")
    top_p = st.slider("Top P", 0.0, 1.0, 0.9, 0.05, key="topp_slider")
    num_predict = st.slider("Max Tokens", 64, 4096, 2048, 64, key="predict_slider")

    # Push slider values into session_state so chat() reads the current values
    st.session_state.temperature = temperature
    st.session_state.top_p = top_p
    st.session_state.num_predict = num_predict

    st.divider()
    if st.button("New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.rerun()

    st.divider()
    st.caption("Private & Local - all data stays on your machine.")


# ── Main area ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>Local LLM Chat</h1>
    <p>Powered by Ollama - Private - Offline</p>
</div>
""", unsafe_allow_html=True)

# Show model info
if models:
    m = next((m for m in models if m["name"] == selected_model), None)
    if m:
        col1, col2, col3 = st.columns(3)
        col1.metric("Size", f"{m.get('size', 0) / 1e9:.1f} GB")
        col2.metric("Modified", m.get("modified_at", "unknown")[:10])
        col3.metric("Details", m.get("details", {}).get("parameter_size", "?"))

# ── Chat history render ──────────────────────────────────────────────────────
container = st.container()

with container:
    for msg in st.session_state.messages:
        cls = "user-message" if msg["role"] == "user" else "assistant-message"
        st.markdown(
            f'<div class="chat-message {cls}">'
            f'<strong>{msg["role"].upper()}</strong><br>{msg["content"]}'
            f'</div>',
            unsafe_allow_html=True,
        )

# ── Input ────────────────────────────────────────────────────────────────────
prompt = st.chat_input("Ask anything ...")

if prompt and online and selected_model:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with container:
        st.markdown(
            f'<div class="chat-message user-message">'
            f'<strong>USER</strong><br>{prompt}</div>',
            unsafe_allow_html=True,
        )

    # Stream assistant response
    with st.spinner(f"Generating with {selected_model} ..."):
        messages = list(st.session_state.messages)
        response = ""
        placeholder = st.empty()

        try:
            for chunk in chat(host, selected_model, messages):
                delta = chunk.get("message", {}).get("content", "")
                response += delta
                placeholder.markdown(
                    f'<div class="chat-message assistant-message">'
                    f'<strong>ASSISTANT</strong><br>{response}</div>',
                    unsafe_allow_html=True,
                )
        except Exception as e:
            st.error(f"Error: {e}")
            response = f"[Error: {e}]"

    # Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": response})
    placeholder.empty()
    st.rerun()