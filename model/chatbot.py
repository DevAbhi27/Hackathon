# model/chatbot.py
import os
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()

class Chatbot:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("WARNING: GOOGLE_API_KEY not found. Using mock responses for testing.")
            self.use_mock = True
        else:
            try:
                import google.generativeai as genai
                # Configure Gemini
                genai.configure(api_key=api_key)
                # Use gemini-1.5-flash
                self.model = genai.GenerativeModel("gemini-1.5-flash")
                self.use_mock = False
                print("SUCCESS: Google Generative AI configured successfully")
            except ImportError:
                print("WARNING: google-generativeai not installed. Using mock responses for testing.")
                self.use_mock = True
        
        # Store previous conversation context
        self.context = ""

    def get_response(self, user_message: str) -> str:
        """
        Get AI-generated response as concise numbered options (1, 2, 3, ...),
        strictly travel-related, context-aware, and greeting-aware.
        """
        if self.use_mock:
            return self._get_mock_response(user_message)
        
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
    
    def _get_mock_response(self, user_message: str) -> str:
        """Get mock responses for testing when Google API is not available"""
        user_message_lower = user_message.lower()
        
        # Greeting responses
        if any(word in user_message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
            return """1. Hello! I'm TravelBuddy, your AI travel assistant!
2. I can help you plan amazing trips and discover new destinations
3. What would you like to know about travel today?"""
        
        # Travel destination queries
        elif any(word in user_message_lower for word in ['destination', 'place', 'where', 'travel', 'visit', 'trip']):
            return """1. Historical destinations: Taj Mahal, Red Fort, Qutub Minar
2. Natural wonders: Himalayas, Kerala backwaters, Goa beaches
3. Cultural sites: Golden Temple, Ajanta Caves, Khajuraho"""
        
        # Budget travel
        elif any(word in user_message_lower for word in ['budget', 'cheap', 'affordable', 'cost']):
            return """1. Budget-friendly destinations: Rajasthan, Himachal Pradesh
2. Use local transport: buses, trains, shared taxis
3. Stay in hostels, guesthouses, or homestays"""
        
        # Food and cuisine
        elif any(word in user_message_lower for word in ['food', 'eat', 'cuisine', 'restaurant']):
            return """1. Try local street food for authentic flavors
2. Regional specialties: biryani, dosa, thali, chaat
3. Don't miss: chai, lassi, and regional sweets"""
        
        # Safety and tips
        elif any(word in user_message_lower for word in ['safe', 'safety', 'tip', 'advice', 'help']):
            return """1. Keep copies of important documents
2. Stay connected with local emergency numbers
3. Pack light and keep valuables secure"""
        
        # Default response
        else:
            return """1. I can help you plan your next adventure!
2. Ask me about destinations, travel tips, or itineraries
3. What kind of travel experience are you looking for?"""
