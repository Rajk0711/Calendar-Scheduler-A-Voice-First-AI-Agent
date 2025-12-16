# Voice-Enabled AI Scheduling Agent (Python Version)

A voice-enabled AI scheduling assistant built with **Python**, **LangGraph**, **Streamlit**, and **Google Gemini**.

## Features
-   **Voice Interface**: Speak to the agent directly in the browser.
-   **AI Brain**: Powered by Google's `gemini-flash-latest` model.
-   **Smart Scheduling**: Integrates with Google Calendar (or uses a Mock Calendar if credentials are missing).
-   **LangGraph Agent**: Orchestrates conversation flow and tool usage.
-   **1.5x Audio Speed**: Faster TTS responses for a snappier experience.

## Prerequisites
-   Python 3.10+
-   [FFmpeg](https://ffmpeg.org/) (Required for audio processing)
    -   Mac: `brew install ffmpeg`
    -   Windows/Linux: Install via package manager.

## Setup

1.  **Navigate to the app directory:**
    ```bash
    cd NextDimensionAI
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Variables:**
    Ensure you have a `.env` file in the root with:
    ```env
    GEMINI_API_KEY=your_api_key_here
    GOOGLE_SERVICE_ACCOUNT_JSON=your_service_account_json (Optional, for real calendar)
    ```

## Usage

Run the Streamlit app:
```bash
streamlit run ui/app.py
```

Open your browser to `http://localhost:8501`.

## Project Structure
-   `ui/`: Frontend components.
    -   `app.py`: Main Streamlit application.
-   `core/`: Backend logic.
    -   `agent.py`: LangGraph agent.
    -   `tools.py`: Calendar tools & Mock Data.
-   `requirements.txt`: Python dependencies.
