# Local LLM Chat

A Streamlit chat interface for [Ollama](https://ollama.com). Runs 100% locally - no data leaves your machine, no API keys, no cloud.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- Streaming chat responses
- Model picker (auto-detects installed Ollama models)
- Temperature, Top-P, and Max Tokens controls
- Model info panel (size, params, modified date)
- New Chat / history reset
- Works on Linux, macOS, and Windows

## Requirements

- [Ollama](https://ollama.com/download) installed and running
- Python 3.10 or newer
- At least one model pulled, e.g. `ollama pull llama3.2:3b`

## Setup

### 1. Install Ollama

Linux / macOS:
```bash
curl -fsSL https://ollama.com/install.sh | sh