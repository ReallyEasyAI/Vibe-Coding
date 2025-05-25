# OpenAI Text-to-Speech Web App

A Streamlit web application that converts text to speech using OpenAI's TTS API.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

3. Run the app:
```bash
streamlit run app.py
```

## Features

- Text input for custom messages
- Multiple voice options (alloy, echo, fable, onyx, nova, shimmer, coral)
- Custom instructions for tone and style
- Audio playback directly in the browser
- Download generated audio files

## Usage

1. Enter your text in the text area
2. Choose a voice from the dropdown
3. Add optional instructions for tone/style
4. Click "Generate Speech" to create the audio
5. Play the audio or download the file
