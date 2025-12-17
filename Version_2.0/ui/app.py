import streamlit as st
import os
import sys
import tempfile
from gtts import gTTS
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

# Add root directory to path to find 'core'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.agent import agent_executor, SYSTEM_PROMPT as BASE_SYSTEM_PROMPT

# Define Personality Prompts
PERSONALITY_PROMPTS = {
    "Professional Executive": """
    Tone: Formal, concise, and efficient.
    Style: Use business terminology. Focus on productivity and clear outcomes.
    Example: "I have scheduled the meeting. Is there anything else?"
    """,
    "Chill Bestie": """
    Tone: Casual, friendly, and enthusiastic. Use emojis! 🌟
    Style: Talk like a helpful friend. Be supportive and relaxed.
    Example: "Got it! Meeting is booked! 🎉 Anything else you need, bestie?"
    """
}

load_dotenv()

# Construct absolute path to logo
logo_path = os.path.join(os.path.dirname(__file__), 'logo.png')

st.set_page_config(page_title="AI Scheduling Agent", page_icon=logo_path)

st.image(logo_path, width=80)
st.title("Voice-Enabled AI Scheduling Agent")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for controls
with st.sidebar:
    st.header("Settings")
    
    # 1. Personality Switcher
    selected_personality = st.selectbox(
        "Choose Agent Persona:",
        list(PERSONALITY_PROMPTS.keys()),
        index=0
    )
    
    # Update system prompt based on selection
    current_system_prompt = BASE_SYSTEM_PROMPT + "\n\n" + PERSONALITY_PROMPTS[selected_personality]
    
    # 2. Smart Daily Briefing Button
    if st.button("Brief Me (Smart Summary)"):
        st.session_state['trigger_briefing'] = True

# Handle Briefing Trigger
if st.session_state.get('trigger_briefing', False):
    # We will trigger the processing below, but first let's handle system prompt updates
    pass 

# Update the System Prompt if personality changes
if "last_personality" not in st.session_state:
    st.session_state.last_personality = selected_personality

if st.session_state.last_personality != selected_personality:
    st.session_state.last_personality = selected_personality
    st.session_state.messages = [] # Clear chat to apply new persona cleanly
    st.rerun()

from langchain_core.messages import SystemMessage
if not st.session_state.messages:
    # Initialize with the selected system prompt
    st.session_state.messages.append(SystemMessage(content=current_system_prompt))
else:
    # If messages exist, ensure the first message is the correct SystemMessage
    if isinstance(st.session_state.messages[0], SystemMessage):
        if st.session_state.messages[0].content != current_system_prompt:
             st.session_state.messages[0] = SystemMessage(content=current_system_prompt)


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)

# Function to handle user input (text or audio)
def process_input(user_input):
    # Add user message to chat history
    st.session_state.messages.append(HumanMessage(content=user_input))
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call Agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Prepare state with optimized context window
            # Always keep the first message (likely System Prompt) and the last 10 messages
            if len(st.session_state.messages) > 10:
                short_history = [st.session_state.messages[0]] + st.session_state.messages[-10:]
            else:
                short_history = st.session_state.messages
                
            state = {"messages": short_history}
            result = agent_executor.invoke(state)
            
            # Get last message
            last_message = result["messages"][-1]
            response_text = last_message.content
            
            st.markdown(response_text)
            
            # Add assistant message to history
            st.session_state.messages.append(last_message)
            
            # TTS
            try:
                tts = gTTS(text=response_text, lang='en')
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                    tts.save(fp.name)
                    original_audio_path = fp.name
                
                # Speed up audio using ffmpeg
                output_audio_path = original_audio_path.replace(".mp3", "_fast.mp3")
                import subprocess
                subprocess.run([
                    "ffmpeg", "-i", original_audio_path, 
                    "-filter:a", "atempo=1.75", 
                    "-vn", output_audio_path, "-y"
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # Play faster audio
                st.audio(output_audio_path, format="audio/mp3", autoplay=True)
                
                # Cleanup
                os.remove(original_audio_path)
                # os.remove(output_audio_path) # Streamlit might need it for a bit, let OS handle temp cleanup or delete later
            except Exception as e:
                st.error(f"TTS Error: {e}")

# Audio Input
audio_value = st.audio_input("Speak to the agent")

if audio_value:
    # Transcribe audio (using Google Speech Recognition via SpeechRecognition lib would be ideal, 
    # but for simplicity/dependency minimization, we might need an STT service.
    # Since we didn't install SpeechRecognition, let's assume we need to add it or use a cloud API.
    # Wait, the user requirement said "Voice-Enabled". 
    # Streamlit's st.audio_input returns a file-like object.
    # We need to transcribe it.
    # Let's use Gemini for STT since we have the key!
    
    import google.generativeai as genai
    
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    
    with st.spinner("Transcribing..."):
        try:
            # Save to temp file because Gemini API might need path or bytes
            # genai.upload_file supports path.
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
                tmp_audio.write(audio_value.read())
                tmp_audio_path = tmp_audio.name
            
            # Upload to Gemini
            myfile = genai.upload_file(tmp_audio_path)
            model = genai.GenerativeModel("gemini-flash-latest")
            
            # Prompt for transcription
            result = model.generate_content([myfile, "Transcribe this audio exactly."])
            transcription = result.text
            
            # Process the transcribed text
            process_input(transcription)
            
        except Exception as e:
            st.error(f"Transcription Error: {e}")

# Text Input (Fallback)
if prompt := st.chat_input("How can I help you..."):
    process_input(prompt)

