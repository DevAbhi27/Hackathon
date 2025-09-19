# from flask import Flask, request, jsonify, render_template
# from model.chatbot import Chatbot

# app = Flask(__name__)

# # Create a single instance of Chatbot to reuse
# bot = Chatbot()

# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/chat", methods=["POST"])
# def chat():
#     user_message = request.json.get("message")
#     # Use the Chatbot instance to get a response
#     bot_reply = bot.get_response(user_message)
#     return jsonify({"reply": bot_reply})

# if __name__ == "__main__":
#     app.run(debug=True)
  
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sys
import os

# Import your chatbot model
try:
    from model.chatbot import Chatbot
    print(" Chatbot model imported successfully")
except ImportError as e:
    print(f"  Error importing chatbot: {e}")
    print("Make sure your chatbot.py file is in the model/ directory")
    sys.exit(1)

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Create a single instance of Chatbot to reuse
try:
    bot = Chatbot()
    print(" Chatbot instance created successfully")
except Exception as e:
    print(f" Error creating chatbot instance: {e}")
    sys.exit(1)

@app.route("/")
def index():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Python Flask Chatbot Server",
        "version": "1.0.0"
    })

@app.route("/health", methods=["GET"])
def health():
    """Detailed health check"""
    try:
        # Test if chatbot is working
        test_response = bot.get_response("test")
        return jsonify({
            "status": "healthy",
            "chatbot": "ready",
            "test_response": str(test_response)[:50] + "..." if len(str(test_response)) > 50 else str(test_response)
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "chatbot": "error",
            "error": str(e)
        }), 500

@app.route("/chat", methods=["POST"])
def chat():
    """Main chat endpoint"""
    try:
        # Get the message from request
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                "reply": "Please provide a message",
                "error": "Missing message in request"
            }), 400
        
        user_message = data.get("message", "").strip()
        
        if not user_message:
            return jsonify({
                "reply": "Please provide a non-empty message",
                "error": "Empty message"
            }), 400
        
        print(f" Received message: {user_message}")
        
        # Use the Chatbot instance to get a response
        bot_reply = bot.get_response(user_message)
        
        print(f" Bot reply: {bot_reply}")
        
        # Return the response in the expected format
        return jsonify({
            "reply": str(bot_reply),
            "status": "success"
        })
        
    except Exception as e:
        print(f" Error in chat endpoint: {e}")
        return jsonify({
            "reply": "Sorry, I encountered an error while processing your message. Please try again.",
            "error": str(e),
            "status": "error"
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "status": 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "status": 500
    }), 500

if __name__ == "__main__":
    # Configuration
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    print(f" Starting Python Flask server on port {port}")
    print(f"Debug mode: {debug_mode}")
    
    try:
        app.run(
            host='0.0.0.0',  # Allow connections from other containers/services
            port=port,
            debug=debug_mode,
            threaded=True  # Enable threading for concurrent requests
        )
    except Exception as e:
        print(f"Failed to start Flask server: {e}")
        sys.exit(1)
    print(" Flask server started successfully")