from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS
import logging

# Load environment variables
load_dotenv()

# Constants
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")

# Basic validation
if not GROQ_API_KEY:
    raise ValueError("Missing GROQ_API_KEY in environment.")

# Initialize Flask app
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
CORS(app)  # Enable CORS for cross-domain requests

# Logging setup
logging.basicConfig(level=logging.INFO)

def generate_nepali_text(prompt):
    """Call GROQ API to generate Nepali text."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "तपाईं एक सहायक लेखक हुनुहुन्छ जसले नेपाली भाषामा मात्र उत्तर दिनुहुन्छ।"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except requests.exceptions.RequestException as e:
        logging.error("API Error: %s", e)
        return "API Error: Unable to fetch content."

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/generate', methods=['POST'])
def generate():
    topic = request.form.get("topic", "").strip()
    keywords = request.form.get("keywords", "").strip()
    content_type = request.form.get("type", "").strip().lower()

    if not topic or content_type not in ['story', 'essay', 'caption']:
        return jsonify({"output": "Invalid input provided."}), 400

    # Build the prompt in Nepali to encourage Nepali-language response
    prompt = f"कृपया '{topic}' शीर्षकमा एउटा {content_type} नेपाली भाषामा लेख्नुहोस्। निम्न शब्दहरू समावेश गर्नुहोस्: {keywords}।"

    result = generate_nepali_text(prompt)
    return jsonify({"output": result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
