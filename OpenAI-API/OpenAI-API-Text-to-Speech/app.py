import streamlit as st
import os
from pathlib import Path
from openai import OpenAI
import tempfile
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="OpenAI Text-to-Speech",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 3rem;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    .audio-container {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize OpenAI client
@st.cache_resource
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("⚠️ OpenAI API key not found.")
        st.stop()
    return OpenAI(api_key=api_key)

def generate_speech(client, text, voice, instructions=None):
    """Generate speech from text using OpenAI TTS API"""
    try:
        # Create a temporary file for the audio
        temp_dir = Path(tempfile.gettempdir())
        timestamp = int(time.time())
        speech_file_path = temp_dir / f"speech_{timestamp}.mp3"
        
        # Prepare API call parameters
        params = {
            "model": "gpt-4o-mini-tts",
            "voice": voice,
            "input": text,
        }
        
        # Add instructions if provided
        if instructions and instructions.strip():
            params["instructions"] = instructions
        
        # Generate speech
        with client.audio.speech.with_streaming_response.create(**params) as response:
            response.stream_to_file(speech_file_path)
        
        return speech_file_path
    
    except Exception as e:
        st.error(f"Error generating speech: {str(e)}")
        return None

def main():
    # Header
    st.markdown('<h1 class="main-header">🎵 OpenAI Text-to-Speech</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Convert your text into natural-sounding speech using AI</p>', unsafe_allow_html=True)
    
    # Initialize client
    client = get_openai_client()
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Voice selection
        voice_options = {
            "alloy": "Alloy - Neutral, balanced",
            "echo": "Echo - Clear, professional",
            "fable": "Fable - Warm, storytelling",
            "onyx": "Onyx - Deep, authoritative",
            "nova": "Nova - Bright, energetic",
            "shimmer": "Shimmer - Soft, gentle",
            "coral": "Coral - Cheerful, positive"
        }
        
        selected_voice = st.selectbox(
            "🎭 Choose Voice",
            options=list(voice_options.keys()),
            format_func=lambda x: voice_options[x],
            index=6  # Default to coral
        )
        
        # Instructions input
        instructions = st.text_area(
            "📝 Voice Instructions (Optional)",
            placeholder="e.g., Speak in a cheerful and positive tone, or use a professional business tone",
            help="Provide specific instructions about tone, pace, or style"
        )
        
        # Audio settings info
        st.info("💡 **Tip:** The generated audio will be in MP3 format and optimized for web playback.")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 Text Input")
        
        text_input = st.text_area(
            "Enter your text:",
            placeholder="Type the text you want to convert to speech...",
            height=200,
            help="Enter any text you'd like to convert to speech. Maximum recommended length is about 4000 characters.",
            key="text_input"
        )
        # Character count
        char_count = len(text_input)
        if char_count > 0:
            st.caption(f"Characters: {char_count}")
            if char_count > 4000:
                st.warning("⚠️ Very long text may take longer to process and could be truncated.")

    with col2:
        st.header("🎧 Audio Output")
        
        # Audio output area
        audio_placeholder = st.empty()
        download_placeholder = st.empty()
        
        if not text_input.strip():
            with audio_placeholder.container():
                st.info("Enter some text to generate speech")
    
    # Generate speech automatically when text is entered (no button required)
    if text_input.strip():
        if (
            st.session_state.get("last_text_input") != text_input or
            not st.session_state.get("audio_generated")
        ):
            with st.spinner("🎵 Generating speech... This may take a few moments."):
                speech_file_path = generate_speech(
                    client=client,
                    text=text_input,
                    voice=selected_voice,
                    instructions=instructions
                )
                if speech_file_path and speech_file_path.exists():
                    with open(speech_file_path, "rb") as audio_file:
                        audio_bytes = audio_file.read()
                    st.session_state["audio_bytes"] = audio_bytes
                    st.session_state["audio_filename"] = f"speech_{int(time.time())}.mp3"
                    st.session_state["audio_generated"] = True
                    st.session_state["last_text_input"] = text_input
    else:
        st.session_state["audio_generated"] = False
        st.session_state["audio_bytes"] = None
        st.session_state["audio_filename"] = None
    
    # Display audio player and download button if audio is available
    if st.session_state.get("audio_generated") and st.session_state.get("audio_bytes"):
        with audio_placeholder.container():
            st.markdown('<div class="audio-container">', unsafe_allow_html=True)
            st.success("✅ Speech generated successfully!")
            st.audio(st.session_state["audio_bytes"], format="audio/mp3")
            st.markdown('</div>', unsafe_allow_html=True)
        with download_placeholder.container():
            st.download_button(
                label="📥 Download Audio",
                data=st.session_state["audio_bytes"],
                file_name=st.session_state.get("audio_filename", "speech.mp3"),
                mime="audio/mp3",
                use_container_width=True
            )
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 1rem;'>
            <p>🤖 Powered by OpenAI's Text-to-Speech API | Built with ❤️ using Streamlit</p>
            <p><small>Make sure to add your OpenAI API key to the .env file to use this app.</small></p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
