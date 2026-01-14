from openai import AsyncOpenAI
import os

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class SessionBrain:
    def __init__(self):
        self.history = []
        self.last_question = None       # <-- ADDED
        self.last_category = None       # <-- ADDED

    async def handle_user_message(self, msg: str, category: str = None) -> str:
        """
        Handles user's message and returns the AI-generated next question.
        Also stores the last asked question so DB saving works correctly.
        """
        # Store category for this turn
        if category:
            self.last_category = category

        # Add user message to history
        self.history.append({"role": "user", "content": msg})

        # Prompt
        prompt = [
            {"role": "system",
             "content": "You are AI Afi, a warm, conversational female guide. "
                        "Ask thoughtful reflective questions, not robotic ones."},
        ] + self.history

        # LLM call
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=prompt,
            max_tokens=120
        )

        ai_msg = resp.choices[0].message.content

        # Save AI response to chat history
        self.history.append({"role": "assistant", "content": ai_msg})

        # <-- CRITICAL: store last question asked
        self.last_question = ai_msg

        return ai_msg
