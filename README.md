# Alex - AI English Tutor

Alex is an intelligent English tutoring assistant that helps you improve your spoken and written English through natural conversation. It acts like a personal IELTS coach, correcting grammar mistakes while engaging in meaningful discussions about any topic you choose.

## Features

- **🎯 Grammar Correction**: Identifies and corrects grammar, spelling, and phrasing errors
- **🗣️ Voice & Text Input**: Choose to speak or type your messages
- **🔊 Text-to-Speech**: Alex speaks back to you with natural voice
- **💬 Conversational AI**: Engages in natural conversations about any topic
- **📚 Educational**: Explains grammar rules in a friendly, encouraging way
- **🧠 Smart Memory**: Remembers conversation context for natural flow
- **⚡ Powered by Groq**: Uses advanced Llama 3.3 70B model for accurate responses

## Prerequisites

- **Python 3.8+**
- **Groq API Key** (free at https://console.groq.com/)
- **Microphone** (for voice input)
- **Speakers/Headphones** (for voice output)

## Installation

### 1. Clone or Download
```bash
git clone <repository-url>
cd english-mentor
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up API Key
Edit `Final_Version.py` and replace the API key on line 15:
```python
GROQ_API_KEY = "your_groq_api_key_here"
```

**Get your free Groq API key:**
1. Visit https://console.groq.com/
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key
5. Copy and paste it into the code

## How to Run

```bash
python Final_Version.py
```

## How to Use

### 1. **Start the Program**
- Run the command above
- Alex will greet you and explain the options

### 2. **Choose Input Method**
- **Option 1 (Voice)**: Press Enter to start recording, press Enter again to stop
- **Option 2 (Text)**: Type your message directly

### 3. **Practice English**
- Say or type anything in English
- Alex will correct any mistakes and explain them
- Alex will then continue the conversation naturally

### 4. **Exit**
- Type or say: `exit`, `quit`, `bye`, `goodbye`, or `stop`

## Example Interactions

### Grammar Correction Example:
**You:** "How is you? I have three book."  
**Alex:** "You said 'How is you? I have three book' but it should be 'How are you? I have three books.' We use 'are' with 'you' and 'books' is plural. I'm doing great, thanks for asking! What kind of books do you enjoy reading?"

### Perfect Grammar Example:
**You:** "What do you think about cricket?"  
**Alex:** "Perfect grammar! Cricket is such a fascinating sport with incredible strategy and skill involved. Are you a fan of any particular team or player?"

## Project Structure

```
english-mentor/
├── Final_Version.py      # Main program file
├── utils/
│   └── audio_2.py       # Audio recording and processing
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Voice Setup

The program automatically detects available voices and selects the second voice (usually male). If you want to change this:

1. Run the program once to see available voices
2. Note the voice you prefer from the list
3. The voice selection happens automatically

## Troubleshooting

### Common Issues:

**"No module named 'openai'"**
```bash
pip install openai
```

**"No module named 'whisper'"**
```bash
pip install openai-whisper
```

**TTS (Text-to-Speech) not working**
- On Windows: Make sure SAPI5 voices are installed
- On Linux/Mac: Install espeak or festival
```bash
# Linux
sudo apt install espeak espeak-data

# Mac
brew install espeak
```

**Microphone not working**
- Check microphone permissions
- Ensure microphone is not being used by other applications
- Test with other audio applications first

**API Key errors**
- Verify your Groq API key is correct
- Check if you have credits remaining (free tier has limits)
- Ensure internet connection is stable

**"Module 'torch' not found"**
```bash
pip install torch torchvision torchaudio
```

### Performance Tips:

- **Internet Required**: The program needs internet for Groq API calls
- **First Run**: Whisper model download may take a few minutes initially
- **Audio Quality**: Use a good microphone for better speech recognition
- **Quiet Environment**: Background noise can affect speech recognition

## Technical Details

- **AI Model**: Llama 3.3 70B Versatile (via Groq)
- **Speech Recognition**: OpenAI Whisper (base model)
- **Text-to-Speech**: pyttsx3 with system voices
- **Audio Processing**: sounddevice + soundfile
- **Response Time**: ~1-3 seconds for most queries

## API Usage

The program uses Groq's free tier which includes:
- Fast inference with Llama models
- Generous free usage limits
- No credit card required for basic usage

## Educational Value

Alex is designed to help with:
- **IELTS Preparation**
- **Grammar Practice**
- **Pronunciation Feedback**
- **Conversational English**
- **Confidence Building**
- **Real-world English Usage**

## Contributing

Feel free to suggest improvements or report issues. This is an educational tool designed to make English learning engaging and effective.

## License

This project is for educational purposes. Please respect the terms of service of the APIs used (Groq, OpenAI).

---

**Happy Learning! 🎓**

Start your English improvement journey with Alex today. Remember, the best way to learn a language is through conversation and practice!
