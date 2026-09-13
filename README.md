# Local LLM Chat

A Streamlit chat interface for [Ollama](https://ollama.com). Runs 100% locally - no data leaves your machine, no API keys, no cloud.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red)
![License](https://img.shields.io/badge/license-MIT-green)

## Screenshot

![Local LLM Chat Interface](assets/screenshot.png)

## Features

- Streaming chat responses
- Model picker (auto-detects installed Ollama models)
- Temperature, Top-P, and Max Tokens controls
- Model info panel (size, params, modified date)
- New Chat / history reset
- Works on Linux, macOS, and Windows

## Architecture

The application operates on a simple client-server model, optimized for local execution and real-time streaming.

```mermaid
graph TD
    %% Entities
    User([User])
    Streamlit[Streamlit App - app.py]
    OllamaServer[Ollama Server - localhost:11434]
    LLM[Local LLM - llama3.2:3b]

    %% Internal Streamlit Components
    subgraph Streamlit App
        UI[UI Renderer - HTML/CSS]
        Sidebar[Sidebar Controls]
        SessionState[(Session State)]
        APIClient[Ollama API Client]
    end

    %% Flow
    User -->|Interacts with UI| Sidebar
    User -->|Submits Prompt| UI
    
    Sidebar -->|Sets Host, Model, Parameters| SessionState
    UI -->|Appends User Message| SessionState
    SessionState -->|Payload: Messages + Options| APIClient

    APIClient -->|GET /api/tags| OllamaServer
    APIClient -->|POST /api/chat stream=true| OllamaServer

    OllamaServer -->|Loads Model Weights| LLM
    LLM -->|Generates Tokens| OllamaServer
    OllamaServer -->|Streams JSON Chunks| APIClient

    APIClient -->|Updates Response String| UI
    UI -->|Renders Chat Bubbles| User
    SessionState -->|Appends Assistant Response| SessionState
