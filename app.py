from flask import Flask, request, jsonify, render_template
from model.chatbot import Chatbot

app = Flask(__name__)

# Create a single instance of Chatbot to reuse
bot = Chatbot()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    # Use the Chatbot instance to get a response
    bot_reply = bot.get_response(user_message)
    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)
  
