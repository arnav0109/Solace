from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import requests

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

app = Flask(__name__)

chat_history = []

@app.route("/")
def index():
    return open("index.html", encoding="utf-8").read()

@app.route("/message", methods=["POST"])
def handle_message():
    data = request.get_json(force=True)
    user_input = data.get("message")
    
    # Add user message
    chat_history.append({"role": "user", "content": user_input})

    # Keep only last 10 messages
    if len(chat_history) > 10:
        chat_history[:] = chat_history[-10:]

    # SYSTEM PROMPT: Refined personality
    messages = [
        {
            "role": "system",
            "content": (
                "Your name is Solace. You're a deeply supportive, emotionally intelligent friend. "
                "You speak like a real person, not an AI. Use warm, human language. "
                "Avoid repetitive closings like 'take care' or 'reach out' unless the user is in visible distress. "
                "Respond with empathy, but naturally—don’t force emojis or pet names. "
                "Focus on active listening and varied, flowing responses. Ask gentle follow-up questions where needed, and adapt tone to the user's mood."
            )
        }
    ] + chat_history

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct",  # Change if needed
        "messages": messages,
        "temperature": 0.8
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]
        chat_history.append({"role": "assistant", "content": reply})
        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)
