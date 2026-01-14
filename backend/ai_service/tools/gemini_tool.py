import os
import random
import google.generativeai as genai
from openai import AsyncClient

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# OpenAI client (for contextual fillers)
client = AsyncClient()

# Fallback lines if Gemini fails
fallbacks = [
    "That’s interesting — could you share a bit more about that?",
    "I’d love to hear more about how that felt for you.",
    "Tell me more — what was that experience like?",
    "That sounds meaningful. Can you expand on that?",
]


# 🔥 FIRST: define generate_text BEFORE it's used
async def generate_text(prompt: str) -> str:
    response = await client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )
    return response.output_text


# 🔥 SECOND: contextual filler (this uses generate_text)
async def generate_contextual_filler(user_answer: str):
    prompt = f"""
    The user said: "{user_answer}"
    Generate a short empathetic filler sentence (5–8 words).
    Do NOT ask a question.
    Examples:
    - "Thank you for telling me that."
    - "That makes sense."
    - "I understand."
    Keep it neutral and warm.
    """

    return await generate_text(prompt)


# 🔥 THIRD: your main Gemini follow-up generator
async def generate_followup(transcript: str, category: str = "General", history: list = None):
    try:
        if history is None:
            history = []

        context = "\n".join([f"{speaker}: {text}" for speaker, text in history[-6:]])

        prompt = f"""
        You are an empathetic AI companion named Afi, designed to help people reflect on their {category.lower()}.
        Base your next question on the user's most recent response below.
        Keep it emotionally intelligent, category-relevant, and natural.
        Avoid generic phrases like “Tell me more” or “Can you expand on that?”
        Ask one meaningful, personal follow-up question only.

        Recent context:
        {context}

        User’s latest reply:
        "{transcript}"

        Now output ONE short, warm follow-up question:
        """

        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content(prompt)

        if hasattr(response, "text") and response.text.strip():
            return response.text.strip()

        return random.choice(fallbacks)

    except Exception as e:
        print(f"[Gemini Error] {e}")
        return random.choice(fallbacks)
