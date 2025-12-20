# Version 1.0 Architecture Flowchart

This flowchart illustrates the high-level interaction between the user interface, the AI agent, and the calendar/logging systems.

```mermaid
graph TD
    User([User]) -->|Voice/Text| UI[Streamlit UI]
    UI -->|Audio File| STT[Gemini STT Transcription]
    STT -->|Text| AI[LangGraph Agent]
    UI -->|Text Input| AI
    
    subgraph Core "Core Logic"
        AI -->|Decision| Agent[Chatbot Node]
        Agent -->|Tool Call| Tools[Tools Node]
        Tools -->|Action| GoogleCal[Google Calendar API]
        Tools -->|Read/Write| Logs[(event_logs Folder)]
        Tools -->|Cleanup| FS[Filesystem Cleanup]
    end
    
    AI -->|Response Text| TTS[gTTS Text-to-Speech]
    TTS -->|Audio| UI
    AI -->|Response Text| UI
    UI -->|Display/Play| User
    
    Sidebar[Sidebar Controls] -->|Personality/Briefing| UI
    UI -->|Update Prompt| AI
```