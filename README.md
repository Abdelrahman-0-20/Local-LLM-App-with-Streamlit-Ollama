# Local LLM Chat

A Streamlit chat interface for [Ollama](https://ollama.com). Runs 100% locally - no data leaves your machine, no API keys, no cloud.


## Screenshots

<p align="center">
  <img src="LLM1.png" alt="Main Interface" width="48%">
  <img src="LLM2.png" alt="Chat Response" width="48%">
</p>

## Features

- Streaming chat responses
- Model picker (auto-detects installed Ollama models)
- Temperature, Top-P, and Max Tokens controls
- Model info panel (size, params, modified date)
- New Chat / history reset
- Works on Linux, macOS, and Windows

## Architecture

The application operates on a simple client-server model, optimized for local execution and real-time streaming.

```text
+-----------------------+
|         User          |
+-----------------------+
           |
           | Inputs Prompt / Adjusts Settings
           v
+-----------------------+
|   Streamlit Frontend  |
|     (app.py)          |
+-----------------------+
           |
           | 1. Constructs JSON Payload
           |    (messages, temperature, top_p, num_predict)
           |
           | 2. HTTP POST /api/chat (stream=true)
           v
+-----------------------+
|    Ollama Server      |
|  (localhost:11434)    |
+-----------------------+
           |
           | 3. Processes Payload
           v
+-----------------------+
|      Local LLM        |
|     (llama3.2:3b)     |
+-----------------------+
           |
           | 4. Generates Tokens sequentially
           | 5. Streams JSON chunks back to Streamlit
           v
+-----------------------+
|   Streamlit Frontend  |
|  Updates UI in real-  |
|  time via placeholder |
+-----------------------+
           |
           | 6. Saves assistant response
           |    to session state
           v
+-----------------------+
|         User          |
|    Views Response     |
+-----------------------+




## How It Works

1. **Frontend (Streamlit):** Manages the UI, sidebar settings, and conversation history using `session_state`.
2. **API Communication:** Sends HTTP requests to the local Ollama server. Queries `/api/tags` for available models and POSTs prompts to `/api/chat`.
3. **Backend (Ollama):** Receives the payload, loads the specified model into memory, and generates text.
4. **Streaming:** Uses `stream=true` to receive small JSON chunks from Ollama, creating a real-time typing effect in the UI.
5. **State Management:** Appends the completed response to `session_state.messages` to preserve chat history.

## Requirements

- [Ollama](https://ollama.com/download) installed and running
- Python 3.10 or newer
- At least one model pulled, e.g., `ollama pull llama3.2:3b`

## Setup

### 1. Install Ollama

**Linux / macOS:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
