# Voice-Enabled AI Scheduling Agent (Python Version)

A voice-enabled AI scheduling assistant built with **Python**, **LangGraph**, **Streamlit**, **Gemini**and **DeepSeek**(via Hugging Face router) and **Whisper**(via Hugging Face API).

---------------
Version_1 : 
- This folder contains the initial version of the project.
- where it was just a simple voice enabled AI scheduling agent.
- It was storing the events in .txt file locally.
- It was not using any calendar integration.
- I have used **gemini flash** for voice to text conversion.
- Also I have used **gemini flash** as the brain of the agent.
- Due to limited API calls, this agent was not able to perform complex tasks.
---------------
Version_2 :
- This folder contains the updated version of the project.
- It uses **Hugging Face API** to call **DeepSeek-V3.2** for reasoning and task planning.
- It uses **Hugging Face API** to call **openai/whisper-large-v3-turbo** for Speech-to-Text (STT) conversion, replacing Gemini to avoid quota limitations.
- I have used **DeepSeek-V3.2** as the brain of the agent.
- I have used **openai/whisper-large-v3-turbo** for speech to text (STT) conversion.
- I have used **LangGraph** to orchestrate the model calls.
- It features an advanced UI with sidebar controls (Daily Briefing, Today's Agenda).
- It integrates with **Google Calendar** for real-time scheduling (Create, Update, Delete).
---------------

## Project Functionalities (Human-Readable Overview)

### Front-End / User Experience
- **Voice-Interactive UI** — Users interact with the assistant by speaking naturally.
- **Speech-to-Text (STT)** — Converts spoken words into text using **Hugging Face Whisper**.
- **Text-to-Speech (TTS)** — Spoken output using **gTTS** (with 1.75x speedup).
- **Streamlit Interface** — A simple web UI for easy access.

### Functional Tools & Integrations
#### Calendar Tools (Google Calendar Integration)
Connects with your Google Calendar to:
- Check free times
- Create events
- Update or cancel events (real-time IST scheduling)
- **Note**: Email service is not working as of now — this feature is present in the code but not functional.

#### LLMs & AI Technology
- **Hugging Face Whisper** — For high-accuracy Speech-to-Text transcription.
- **DeepSeek-V3.2 (via Hugging Face API)** — A reasoning-focused open LLM used for complex understanding and task planning.
- **LangGraph framework** — To orchestrate model calls, manage workflows, and trigger tools.

### Agent Capabilities
#### Scheduling & Calendar Management
The AI agent can:
- Check your calendar availability
- Schedule new events
- Modify existing events based on follow-up voice instructions
- Handles multi-turn conversations, understands context, and asks follow-ups when needed.

### Technology Stack
This project uses:
- **Streamlit** – Front-end UI
- **LangGraph** – Agent orchestration
- **DeepSeek-V3.2** – AI Reasoning Brain
- **Hugging Face Whisper** – Speech-to-Text transcription
- **Hugging Face API** – To call DeepSeek & Whisper
- **Google Calendar API** – For event scheduling
- **Python** – Backend logic

---

## Technical Setup

### Prerequisites
- Python 3.10+
- [FFmpeg](https://ffmpeg.org/) (Required for audio processing)
    - Mac: `brew install ffmpeg`
    - Windows/Linux: Install via package manager.

### Installation & Setup

1. **Navigate to the project directory:**
    ```
    git clone "github URL"
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
4. **create the client_secrets.json file:**

5. **create the google refresh token:**
    ```
    python3 create_refresh_token.py
    ```
6. **Environment Variables:**
   Create a `.env` file in the root with the following keys (do **not** commit this file):
    ```env
    HUGGINGFACEHUB_API_TOKEN=your_hf_token_here
    GOOGLE_CLIENT_ID=your_google_client_id
    GOOGLE_CLIENT_SECRET=your_google_client_secret
    GOOGLE_REFRESH_TOKEN=your_google_refresh_token
    EMAIL_ADDRESS=your_email@example.com
    EMAIL_PASSWORD=your_email_password
    PORT=3000
    ```
   The `.gitignore` already excludes `.env` and `client_secrets.json`.[for safety reasons]

### Usage

Run the Streamlit app:
```bash
streamlit run Version_2/ui/app.py
```
Open your browser to `http://localhost:8501`.

---

## 📝 Notes for Users
- **Voice-First Experience**: Built to be a voice-first experience — not just text input.
- **Credentials**: You need Google API credentials (client ID/secret/refresh token) for calendar access.
- **Function Calling**: The DeepSeek model does not natively support function calling; the agent uses the OpenAI‑compatible router endpoint, and LangGraph handles the tool orchestration.
- **Model Switching**: If you need to switch back to a model with native function calling (e.g., Gemini), update the configuration in `Version_2/core/agent.py`.
- **Speech-to-Text (STT)**: The agent uses Hugging Face's Whisper model for speech-to-text transcription.
- **Text-to-Speech (TTS)**: The agent uses gTTS for text-to-speech output.