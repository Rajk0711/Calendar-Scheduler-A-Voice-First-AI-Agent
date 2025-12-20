# Voice-Enabled AI Scheduling Agent (Python Version)

A voice-enabled AI scheduling assistant built with **Python**, **LangGraph**, **Streamlit**, and **DeepSeek** (via Hugging Face router).

## Features
- **Voice Interface**: Speak to the agent directly in the browser.
- **AI Brain**: Powered by DeepSeek V3.2 model accessed through the Hugging Face OpenAI‑compatible router.
- **Smart Scheduling**: Integrates with Google Calendar (or uses a Mock Calendar if credentials are missing).
- **LangGraph Agent**: Orchestrates conversation flow and tool usage.
- **Time‑Friendly Voice Output**: Automatically formats times (e.g., "9 AM to 12 PM") for natural speech.
- **1.5x Audio Speed**: Faster TTS responses for a snappier experience.

## Prerequisites
- Python 3.10+
- [FFmpeg](https://ffmpeg.org/) (Required for audio processing)
    - Mac: `brew install ffmpeg`
    - Windows/Linux: Install via package manager.

## Setup

1. **Navigate to the project directory:**
    ```bash
    cd NextDimensionAI
    ```

2. **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate   # macOS/Linux
    .venv\Scripts\activate    # Windows
    ```

3. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Environment Variables:**
   Create a `.env` file in the root with the following keys (do **not** commit this file):
    ```env
    HUGGINGFACEHUB_API_TOKEN=your_hf_token_here
    GOOGLE_CLIENT_ID=your_google_client_id
    GOOGLE_CLIENT_SECRET=your_google_client_secret
    GOOGLE_REFRESH_TOKEN=your_google_refresh_token
    EMAIL_ADDRESS=your_email@example.com
    EMAIL_PASSWORD=your_email_password
    PORT=3000   # optional, for the OAuth local server
    ```
   The `.gitignore` already excludes `.env` and `client_secrets.json`.

## Usage

Run the Streamlit app:
```bash
streamlit run Version_2/ui/app.py
```
Open your browser to `http://localhost:8501`.

You can now ask the assistant to schedule meetings, check availability, or any other calendar‑related task using natural voice commands.

## Project Structure
- `Version_2/`
  - `core/`: Backend logic.
    - `agent.py`: LangGraph agent with DeepSeek integration.
    - `tools.py`: Calendar tools & mock data.
  - `ui/`: Front‑end components.
    - `app.py`: Main Streamlit application.
  - `Innovation/ideas.txt`: Future feature ideas.
- `requirements.txt`: Python dependencies.
- `.env`: Secret configuration (ignored by Git).
- `.gitignore`: Excludes `.env`, `client_secrets.json`, and other generated files.

## Notes
- The DeepSeek model **does not support function calling**; the agent uses the OpenAI‑compatible router endpoint which provides stable chat responses. Tool calls are handled by the LangGraph framework.
- If you need to switch back to a model that supports function calling (e.g., Gemini), update the LLM configuration in `Version_2/core/agent.py` accordingly.
