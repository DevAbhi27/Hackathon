# model/chatbot.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()

class Chatbot:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("❌ GOOGLE_API_KEY not found. Please add it to your .env file.")
        
        # Configure Gemini
        genai.configure(api_key=api_key)

        # Use gemini-1.5-flash
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Store previous conversation context
        self.context = ""

    def get_response(self, user_message: str) -> str:
        """
        Get AI-generated response as concise numbered options (1, 2, 3, ...),
        strictly travel-related, context-aware, and greeting-aware.
        """
        # Combine previous context with new message
        prompt_context = f"{self.context}\nUser: {user_message}" if self.context else f"User: {user_message}"

        prompt = f"""
        You are **TravelBuddy**, a smart and friendly AI travel assistant.

        RULES (STRICT):
        1. ONLY provide travel-related answers (destinations, flights, hotels, packing, tips, local food, transport, travel safety, visa info, etc.).
        2. NEVER give unrelated answers (math, coding, health, entertainment, politics, etc.).
        3. ALWAYS respond in a concise **numbered list format**:
           1. Option one
           2. Option two
           3. Option three
        4. NEVER write long paragraphs. Keep each option short (1-2 lines).
        5. If you cannot answer in the travel context, reply exactly:
           "❌ Sorry, I can only help with travel-related questions."
        6. Recognize greetings and respond with a **fresh, varied greeting** each time.
        7. Always reply based on the **context of the previous chat**.
        8. Remember the conversation context for future messages in this session.

        {prompt_context}
        """

        try:
            response = self.model.generate_content(prompt)
            reply = response.text.strip()

            # Safety check: if AI output is invalid, fallback
            if not reply or "❌" in reply or len(reply.splitlines()) < 2:
                reply = "❌ Sorry, I can only help with travel-related questions."

            # Update context for next message
            self.context += f"\nUser: {user_message}\nTravelBuddy: {reply}"

            return reply

        except Exception as e:
            return f"⚠️ Error: {str(e)}"
