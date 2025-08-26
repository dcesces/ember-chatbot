from flask import Flask, send_file, request, jsonify
import json
import re
import requests

app = Flask(__name__)

API_KEY = 'AIzaSyB1e1Jf-LGhuE4WAodOeFOx4d1ALxPQp74'  # Replace with your actual API key
API_URL = 'https://generativelanguage.googleapis.com/v1/models/text-bison:generate'

# Load intents
def load_intents(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

intents = load_intents("treatment.json")

# Match user query to intents
def find_intent_response(user_input, intents):
    # Normalize user input: lowercased and stripped of punctuation
    user_keywords = re.findall(r'\b\w+\b', user_input.lower())

    best_match = None
    best_score = 0

    # Iterate through all intents to find the best match
    for intent in intents['intents']:
        for pattern in intent['patterns']:
            # Normalize patterns: lowercased and stripped of punctuation
            pattern_keywords = re.findall(r'\b\w+\b', pattern.lower())

            # Calculate overlap between user input and pattern keywords
            overlap = len(set(user_keywords) & set(pattern_keywords))

            # If the overlap is greater than the current best score, update the best match
            if overlap > best_score:
                best_match = intent
                best_score = overlap

    # Return the best match response or a fallback message
    if best_match:
        return best_match['responses'][0]
    else:
        return "I'm sorry, I don't understand your question. Can you rephrase?"

#def find_intent_response(user_input, intents):
    #user_input = user_input.lower().strip()
    
    # Iterate through each intent
    #for intent in intents['intents']:
        #for pattern in intent['patterns']:
            # Use an exact match or more specific matching criteria
            #if pattern.lower() == user_input:
                #return intent['responses'][0]
    #return None


# Call Gemini API
def ask_gemini(question):
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    body = {'prompt': question, 'temperature': 0.7, 'max_output_tokens': 150}
    response = requests.post(API_URL, headers=headers, json=body)
    if response.status_code == 200:
        response_data = response.json()
        return response_data['candidates'][0]['text']
    else:
        return f"I'm sorry, I can't understand. Please try again{response.status_code}"

# Serve chat.html directly
@app.route("/")
def index():
    return send_file("index.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    user_input = request.json.get("user_input", "")
    response = find_intent_response(user_input, intents) or ask_gemini(user_input)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
