import os
import json
import requests
import whisper
import pyttsx3
import warnings
import time
from openai import OpenAI
from utils.audio_2 import record_press_enter1,transcribe_audio1

warnings.filterwarnings("ignore",message="FP16 is not supported on CPU; using FP32 instead")

SAMPLE_RATE = 16000
WHISPER_MODEL = "base"
GROQ_API_KEY = "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"
GROQ_MODEL = "llama-3.3-70b-versatile"

class EnglishTutor:
    def __init__(self):
        print("Loading models and initializing...")
        self.whisper_model = whisper.load_model(WHISPER_MODEL)
        self.selected_voice_id = self._get_voice_id()
        self.conversation_history = [
            {
                "role": "system",
                "content": "You are Alex, a friendly and precise AI English tutor. Your primary goal is to identify grammar errors, explain them clearly, and engage the user in conversation."
            }
        ]
        print("English Tutor initialized successfully!")

    def _get_voice_id(self):
        try:
            engine = pyttsx3.init(driverName="sapi5")
        except Exception:
            engine = pyttsx3.init()

        voices = engine.getProperty("voices")
        print("Available voices:")
        for i,voice in enumerate(voices):
            print(f"  {i}: {voice.name} ({voice.id})")

        selected_id = None
        if len(voices) > 1:
            selected_id = voices[1].id
            print(f"\nSUCCESS: Selected voice is '{voices[1].name}'\n")
        else:
            print("WARNING: Only one voice available. Using default.")
            if voices:
                selected_id = voices[0].id
        
        engine.stop()
        del engine
        return selected_id

    def speak(self,text):
        print(f"\nAlex says: {text}")
        try:
            engine = pyttsx3.init(driverName="sapi5") if os.name == 'nt' else pyttsx3.init()
            
            if self.selected_voice_id:
                engine.setProperty("voice",self.selected_voice_id)
            engine.setProperty("rate",165)
            engine.setProperty("volume",1.0)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
            del engine
        except Exception as e:
            print(f"TTS Error: {e}. Could not play audio.")

    def get_user_input(self):
        print("\n" + "="*50)
        print("How would you like to communicate?")
        print("1. Voice (speak)")
        print("2. Text (type)")
        choice = input("Choose (1 or 2): ").strip()
        return self._get_voice_input() if choice == "1" else self._get_text_input()

    def _get_voice_input(self):
        audio_path = record_press_enter1(SAMPLE_RATE, channels=1)
        if not audio_path:
            return None
        transcript,_ = transcribe_audio1(audio_path, self.whisper_model, SAMPLE_RATE)
        if transcript:
            print(f"You said: {transcript}")
        return transcript

    def _get_text_input(self):
        text = input("\nType your message: ").strip()
        return text if text else None

    def call_groq(self,user_text):
        self.conversation_history.append({"role": "user","content": user_text})
        client = OpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )
        system_message = """You are Alex, an expert English tutor. Your task is to analyze the user's message with high accuracy.

RULES:
1. **Analyze Thoroughly**: Check for any grammar, spelling, or phrasing errors.
2. **Correct the Sentence**: Provide a single, fully corrected version.
3. **Determine Error Status**: Set `has_errors` to `true` if even one error is found.
4. **Explain Clearly**: If errors exist, provide a friendly explanation.
5. **Respond Conversationally**: Write a natural response that continues the conversation.

Return ONLY a JSON object with this exact structure:
{
    "corrected_sentence": "The fully corrected sentence.",
    "has_errors": true_or_false,
    "explanation": "A friendly explanation of corrections, or empty string if none.",
    "conversational_response": "Your engaging response to continue the conversation."
}"""

        user_message = f"""USER'S MESSAGE: "{user_text}"

EXAMPLES:
User: "Hello, how is you?"
Output: {{"corrected_sentence": "Hello, how are you?", "has_errors": true, "explanation": "We say 'how are you?' because 'are' is used with 'you'.", "conversational_response": "I'm doing well, thanks! What's on your mind today?"}}

User: "What do you think about Babar Azam?"
Output: {{"corrected_sentence": "What do you think about Babar Azam?", "has_errors": false, "explanation": "", "conversational_response": "Perfect grammar! Babar Azam is an incredible cricketer with such elegant technique. Are you a cricket fan?"}}

Now analyze the message above and return only the JSON."""

        print(f"Making request to Groq API with model: {GROQ_MODEL}")
        
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            print(f"Content from API: {content}")
            
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
            
            print(f"Cleaned content: {content}")
            ai_result = json.loads(content)
            self.conversation_history.append({"role": "assistant", "content": ai_result.get("conversational_response", "")})
            return ai_result
            
        except Exception as e:
            print(f"Groq API error: {e}")
            return {
                "corrected_sentence": user_text, "has_errors": False, "explanation": "",
                "conversational_response": "I'm having a little trouble connecting right now. Let's talk about something else."
            }

    def process_turn(self, user_text):
        ai_result = self.call_groq(user_text)

        has_errors = ai_result.get("has_errors",False)
        explanation = ai_result.get("explanation", "")
        conversational_response = ai_result.get("conversational_response","Let's keep practicing!")
        
        full_response_to_speak = ""
        if has_errors and explanation:
            full_response_to_speak = f"{explanation} {conversational_response}"
        else:
            full_response_to_speak = f"That's perfectly said! {conversational_response}"
            
        self.speak(full_response_to_speak)
        
        print("\n--- Debug Info ---")
        print(f"  Original:   {user_text}")
        print(f"  Corrected:  {ai_result.get('corrected_sentence', 'N/A')}")
        print(f"  Had Errors: {has_errors}")
        if has_errors:
            print(f"  Explanation: {explanation}")
        print("--------------------")
        
        if len(self.conversation_history)>10:
            self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-9:]

    def start_session(self):
        welcome_msg = "Hello! I'm Alex, your English tutor. Let's start our conversation. You can talk about anything you'd like!"
        self.speak(welcome_msg)

        while True:
            try:
                user_input = self.get_user_input()
                if not user_input:
                    self.speak("Sorry, I didn't catch that. Could you please say it again?")
                    continue
                if user_input.lower() in ['exit','quit','bye','goodbye','stop']:
                    self.speak("It was great practicing with you! Keep up the excellent work. Goodbye!")
                    break
                self.process_turn(user_input)
            except KeyboardInterrupt:
                print("\nSession ended by user.")
                self.speak("Session ended. Great job today!")
                break
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                self.speak("Oops, something went wrong. Let's try to continue.")



def run_conversation():
    print("Welcome to Alex - Your Personal English Tutor!")
    tutor = EnglishTutor()
    tutor.start_session()

run_conversation()


