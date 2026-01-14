# ai_service/agents.py
import os
import logging
from crewai.agent import Agent
from crewai.crew import Crew
from crewai.llm import LLM
import google.generativeai as genai
from ai_service.memory_manager import MemoryManager
from ai_service.tools.emotion_tool import EmotionTool

# Instantiate it once so other parts of your app can use it
emotion_tool = EmotionTool()

emotion_result = emotion_tool._run("I feel nervous and hopeful")

print(emotion_result)
# =========================================================
# ⚙️ CONFIGURATION
# =========================================================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    logging.warning("⚠️ GOOGLE_API_KEY not found. Gemini responses may fail.")
else:
    genai.configure(api_key=GOOGLE_API_KEY)

memory = MemoryManager()

# =========================================================
# 🧠 GEMINI WRAPPER
# =========================================================
def use_gemini(prompt: str):
    """Lightweight helper to query Gemini 2.0 Pro."""
    try:
        model = genai.GenerativeModel("models/gemini-2.0-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Gemini call failed: {e}")
        return "[Error: Gemini model failed]"

# =========================================================
# 🧩 DEFINE CORE LLM
# =========================================================
llm = LLM(model="gpt-4o-mini", temperature=0.7)

# =========================================================
# 👥 CREWAI AGENTS
# =========================================================
legacy_curator = Agent(
    name="LegacyCurator",
    role="Guides users through life reflections and legacy questions.",
    goal="Ask thoughtful, emotionally intelligent questions based on user tone and history.",
    backstory="A compassionate conversationalist trained to elicit meaningful personal stories with empathy.",
    verbose=True,
    llm=llm
)

emotion_tracker = Agent(
    name="EmotionTracker",
    role="Analyzes emotional state from language and tone.",
    goal="Detect emotions and mood shifts in the user's speech or text input.",
    backstory="A gentle psychologist AI that listens deeply and identifies underlying emotions accurately.",
    verbose=True,
    llm=llm
)

memory_weaver = Agent(
    name="MemoryWeaver",
    role="Connects current responses to earlier reflections.",
    goal="Preserve conversational continuity and link present moments with past experiences.",
    backstory="A storyteller AI that weaves past and present memories into a cohesive emotional narrative.",
    verbose=True,
    llm=llm
)

# =========================================================
# 🎛 CREW ORCHESTRATION
# =========================================================
crew = Crew(
    agents=[legacy_curator, emotion_tracker, memory_weaver],
    verbose=True
)

# =========================================================
# 🔁 MAIN FUNCTION — ADAPTIVE QUESTION GENERATOR
# =========================================================
def get_next_question(user_id=None, last_response=None, detected_emotion="neutral"):
    """Generate the next reflective question based on memory and emotional context."""
    user_id = user_id or "anonymous"
    previous_turns = memory.recall(user_id)

    context_snippet = "\n".join([
        f"User: {t['user']}\nAI: {t['ai']}\nEmotion: {t['emotion']}"
        for t in previous_turns[-3:]
    ])

    prompt = f"""
    Conversation history:
    {context_snippet}

    Latest response: "{last_response}"
    Detected emotion: {detected_emotion}

    Based on this, generate one warm, empathetic, open-ended question
    that invites the user to share more about their thoughts or memories.
    """

    question = use_gemini(prompt)

    # Save interaction context
    memory.add_turn(
        user_id=user_id,
        user_message=last_response or "",
        ai_reply=question,
        emotion=detected_emotion
    )

    return {"next_question": question.strip()}

# =========================================================
# 🧪 TEST (Optional Manual Run)
# =========================================================
if __name__ == "__main__":
    print(get_next_question("test_user", "I used to play piano with my grandmother.", "nostalgic"))
