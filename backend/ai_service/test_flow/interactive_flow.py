from openai import AsyncOpenAI
from ai_service.test_flow.qa_stt_tool import qa_speech_to_text
from ai_service.tools.text_to_speech_tool import synthesize_speech

client = AsyncOpenAI()

CATEGORY_QUESTIONS = {
    "Introduction": "Can you tell me a bit about yourself?",
    "Wisdom (About You)": "What values guide your life the most?",
    "Places": "Is there a place that holds special meaning for you?",
    "Life Events - Early Childhood": "What’s your earliest memory?",
    "Life Events - Teen": "What was your teenage self like?",
    "Life Events - Post Secondary": "Tell me more about that part of your life.",
    "Life Events - Adulthood": "What’s one important lesson adulthood taught you?",
    "Life Events - Present": "How would you describe your life today?",
    "Family - Partner": "How did you and your partner meet?",
    "Family - Past Partners": "What did past relationships teach you?",
    "Family - Children": "What does being a parent mean to you?",
    "Family - Parenting": "What has parenting taught you about love or patience?",
    "Family - Family General": "How would you describe your family dynamic?",
    "Family - Mother": "What’s something your mother taught you that stayed with you?",
    "Family - Father / Parents": "How would you describe your relationship with your parents?",
    "Family - Siblings": "What’s your relationship like with your siblings?",
    "Family - Grandparents": "What role did your grandparents play in your life?",
    "Family - Pets": "How has a pet impacted your life or emotions?",
}


# ---------------------- Start Conversation ----------------------
async def start_conversation_for_category(category: str):
    question = CATEGORY_QUESTIONS.get(category, "Tell me more about that part of your life.")
    audio_data = await synthesize_speech(question)
    return {
        "category": category,
        "first_question_text": question,
        "first_question_audio": audio_data.get("base64", ""),
    }


# ---------------------- Continue Conversation ----------------------
async def continue_conversation(category: str, audio_path: str):
    try:
        transcript = await qa_speech_to_text(audio_path)
        if not transcript or transcript.strip() == "":
            next_q = "Could you please repeat that? I didn’t quite catch it."
            tts = await synthesize_speech(next_q)
            return {
                "transcript": "(no transcript)",
                "ai_reply": "",
                "next_question_text": next_q,
                "next_question_audio": tts.get("base64", ""),
            }

        # Summarize
        summary_prompt = f"Summarize this in one warm sentence:\n{transcript}"
        summary_res = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": summary_prompt}],
            max_tokens=60,
        )
        summary = summary_res.choices[0].message.content.strip()

        # Generate next question
        follow_prompt = f"The user said: '{summary}'. Ask a natural, empathetic follow-up question."
        next_res = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": follow_prompt}],
            max_tokens=60,
        )
        next_q = next_res.choices[0].message.content.strip()
        if not next_q:
            next_q = "That’s interesting. Can you tell me a bit more about that?"

        # Voice for next question
        tts = await synthesize_speech(next_q)

        return {
            "transcript": transcript,
            "ai_reply": summary,
            "next_question_text": next_q,
            "next_question_audio": tts.get("base64", ""),
        }
    except Exception as e:
        print(f"❌ Conversation error: {e}")
        return {
            "error": str(e),
            "transcript": "",
            "ai_reply": "",
            "next_question_text": "Sorry, I had trouble understanding that.",
            "next_question_audio": (await synthesize_speech("Sorry, I had trouble understanding that.")).get("base64", ""),
        }


# ---------------------- Compatibility Wrapper ----------------------
async def run_conversation(patient_id: str, category: str):
    return await start_conversation_for_category(category)
