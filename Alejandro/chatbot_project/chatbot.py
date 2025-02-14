from flask import Flask, request, render_template
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

# Define the chatbot function to get a response from OpenAI
def chatbot(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # or "gpt-4" if you have access
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Define the route that handles both GET and POST requests
@app.route("/", methods=["GET", "POST"])
def index():
    chatbot_reply = None
    if request.method == "POST":
        user_message = request.form["message"]  # Get the message from the form
        chatbot_reply = chatbot(user_message)  # Send it to the chatbot function and get the reply
    return render_template("index.html", chatbot_reply=chatbot_reply)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
