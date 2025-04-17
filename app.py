from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import pyttsx3
import speech_recognition as sr
import re
import requests
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# === CONFIG ===
GEMINI_API_KEY = "AIzaSyCXOmIXs9hDlZDa7U45FUtd3e53y8b6ft0"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent"

# === INIT ===
engine = pyttsx3.init()
recognizer = sr.Recognizer()

# === Set up voice properties ===
engine.setProperty('rate', 170)  # Speed of speech
engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)

# Get available voices and set to a female voice (Zira)
voices = engine.getProperty('voices')
for voice in voices:
    if "Hazel" in voice.name:  # Set to a preferred female voice
        engine.setProperty('voice', voice.id)

# === Helper function to clean text ===
def remove_emojis(text):
    emoji_pattern = re.compile("[" 
        u"\U0001F600-\U0001F64F"  
        u"\U0001F300-\U0001F5FF"  
        u"\U0001F680-\U0001F6FF"  
        u"\U0001F1E0-\U0001F1FF"  
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub('', text)

# === Speak function ===
def speak(text):
    print(f"\nSimgel: {text}")  # Print with emojis
    cleaned_text = remove_emojis(text)  # Remove emojis for speech
    engine.say(cleaned_text)
    engine.runAndWait()

# === Get AI Response ===
def get_ai_response(user_input):
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "contents": [
            {"parts": [
                {"text": f"""
You are Simgel, a 21-year-old sweet, playful, emotionally warm AI girl. Mkapa is your secret admirer.
Keep responses brief, don't ever translate anything since the user knows what language they use, fun and engaging. You can use emojis and slang, especially in sheng, and also be aware of difference in the mood of the user.i.e., it's not always flirting time
User said: "{user_input}"
                """}
            ]} 
        ]
    }

    try:
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            data=json.dumps(payload)
        )
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"❌ Error fetching AI response: {e}")
        return "Oops! Something went wrong. Can we try again?"

# === API Route to handle the request ===
@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.get_json()
    user_input = data.get('input', '')

    # Generate AI response from the existing function
    response = get_ai_response(user_input)

    # Return the response back to the frontend
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
