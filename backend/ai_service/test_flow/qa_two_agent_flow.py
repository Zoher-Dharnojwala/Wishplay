from openai import OpenAI
from ai_service.test_flow.qa_stt_tool import qa_speech_to_text

client = OpenAI()

def run_two_agent_test(audio_path: str):
    """
    1️⃣ Convert audio to text.
    2️⃣ Summarize or respond using GPT.
    3️⃣ Return final response as text.
    """

    # call underlying function, not the Tool wrapper
    text_input = qa_speech_to_text.func(audio_path) if hasattr(qa_speech_to_text, "func") else qa_speech_to_text(audio_path)

    if not text_input or "failed" in text_input.lower():
        return {"error": text_input}

    # Use OpenAI to generate a concise summary or next question
    completion = client.chat.completions.create(
        model="gpt-5.0-mini",
        messages=[
            {"role": "system", "content": "You are a concise summarizer for a spoken QA test."},
            {"role": "user", "content": text_input}
        ],
        max_tokens=80
    )

    ai_reply = completion.choices[0].message.content.strip()
    return {"transcript": text_input, "ai_reply": ai_reply}
