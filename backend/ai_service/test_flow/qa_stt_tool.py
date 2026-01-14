from openai import AsyncOpenAI

client = AsyncOpenAI()

async def qa_speech_to_text(audio_path: str) -> str:
    """
    Converts an audio file to text (async) using OpenAI Whisper model.
    """
    try:
        with open(audio_path, "rb") as audio_file:
            transcript = await client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=audio_file
            )
        return transcript.text.strip()
    except Exception as e:
        print(f"❌ STT failed: {e}")
        return "(no transcript)"
