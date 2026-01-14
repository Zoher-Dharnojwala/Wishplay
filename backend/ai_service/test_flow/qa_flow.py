from ai_service.test_flow.qa_agent import qa_agent
from ai_service.test_flow.qa_stt_tool import qa_speech_to_text
from ai_service.test_flow.qa_tts_tool import qa_text_to_speech

def run_qa_test_flow(audio_input_path: str):
    # 1️⃣ Convert audio question to text
    question_text = qa_speech_to_text(audio_input_path)
    print(f"🗣️ Question transcribed: {question_text}")

    # 2️⃣ Generate short answer using the agent
    answer_text = qa_agent.run(f"Answer this question clearly and briefly: {question_text}")
    print(f"🤖 Answer generated: {answer_text}")

    # 3️⃣ Convert answer back to speech
    answer_audio_path = qa_text_to_speech(answer_text)
    print(f"🎧 Audio saved to: {answer_audio_path}")

    return answer_audio_path
