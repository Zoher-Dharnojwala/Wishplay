import json
import random
from pathlib import Path
from openai import AsyncOpenAI

client = AsyncOpenAI()

class LifeReviewSession:

    def __init__(self, category: str):
        self.category = category.strip()

        # Load *category-specific* question file
        self.question_db = self._load_category_questions()

        # Conversation progression
        self.asked_ids = set()
        self.last_question_id = None
        self.memory = []
        self.max_history = 4


    # --------------------------------------------
    # LOAD QUESTIONS BY CATEGORY
    # --------------------------------------------
    def _load_category_questions(self):
        """
        Loads the correct JSON file based on category.
        Falls back to About You if missing.
        """

        root = Path(__file__).parent.parent / "knowledge"

        # Mapping categories → JSON filenames
        file_map = {
            "Introduction": "introduction.json",
            "Wisdom": "wisdom.json",
            "Places": "places.json",
            "Early Childhood": "early_childhood.json",
            "Teen": "teen.json",
            "Post Secondary": "post_secondary.json",
            "Adulthood": "adulthood.json",
            "Present": "present.json",
            "Family": "family.json",
        }

        # Default fallback
        default_file = "screening_questions.json"

        filename = file_map.get(self.category, default_file)
        path = root / filename

        if not path.exists():
            print(f"⚠ Category file not found: {filename}, using fallback.")
            path = root / default_file

        with open(path, "r") as f:
            return json.load(f)


    # --------------------------------------------
    # PUBLIC ENTRY POINT
    # --------------------------------------------
    async def handle_user_message(self, user_text: str) -> str:

        self._store_memory("user", user_text)

        emotion = await self._detect_emotion(user_text)

        # SADNESS OVERRIDE
        if emotion == "sadness":
            reply = self._sadness_reply(user_text)
            self._store_memory("ai", reply)
            return reply

        # NORMAL FLOW
        next_q = self._get_next_question(emotion)

        clean_q = self._clean_question(next_q["prompt"])
        self.last_question_id = next_q["id"]
        self._store_memory("ai", clean_q)

        return clean_q


    # --------------------------------------------
    # EMOTION DETECTION
    # --------------------------------------------
    async def _detect_emotion(self, text: str) -> str:
        prompt = f"""
Classify the emotion of this message into ONE category:
joy, neutral, stress, sadness, nostalgia, pride, regret, curiosity, faith, trust, values, growth, creativity, inspiration, ambition, hope.

Only output the emotion. No punctuation.
Message: "{text}"
"""
        try:
            res = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3,
                temperature=0
            )
            emotion = res.choices[0].message.content.lower().strip()
            return emotion or "neutral"
        except:
            return "neutral"


    # --------------------------------------------
    # SADNESS HANDLER
    # --------------------------------------------
    def _sadness_reply(self, user_text: str) -> str:
        followups = [
            "That sounds really heavy. Do you feel okay talking more about it?",
            "I hear how difficult that feels. Would you like to continue?",
            "Thank you for sharing that with me. Want to talk about it more?"
        ]

        crisis_terms = ["suicide", "kill myself", "end my life", "self-harm"]
        if any(term in user_text.lower() for term in crisis_terms):
            return (
                "I'm really sorry you're feeling this way. I care about your safety, "
                "but I'm not trained to give crisis support. Please consider talking to "
                "a trained professional or someone you trust. "
                "Would you like to continue our conversation gently?"
            )
        return random.choice(followups)


    # --------------------------------------------
    # GET NEXT QUESTION *FILTERED BY CATEGORY*
    # --------------------------------------------
    def _get_next_question(self, emotion: str) -> dict:

        unused = [q for q in self.question_db if q["id"] not in self.asked_ids]

        if not unused:
            return {
                "id": "done",
                "prompt": "Thank you. That covers everything for this section."
            }

        # Emotion-matched suggestions
        emotional_match = [
            q for q in unused
            if emotion in q["emotion_tags"] or "neutral" in q["emotion_tags"]
        ]

        pool = emotional_match if emotional_match else unused

        # Sort by priority
        pool = sorted(pool, key=lambda x: x["priority"])

        chosen = pool[0].copy()
        chosen["prompt"] = random.choice(chosen["prompt_variants"])

        self.asked_ids.add(chosen["id"])

        return chosen


    # --------------------------------------------
    # MEMORY STORAGE
    # --------------------------------------------
    def _store_memory(self, speaker, text):
        self.memory.append({"speaker": speaker, "text": text})
        if len(self.memory) > self.max_history:
            self.memory.pop(0)


    # --------------------------------------------
    # CLEAN QUESTION
    # --------------------------------------------
    def _clean_question(self, text: str) -> str:
        if "?" in text:
            text = text.split("?")[0] + "?"
        words = text.split()
        if len(words) > 30:
            text = " ".join(words[:30]) + "?"
        return text.strip()
