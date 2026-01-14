import os
import tempfile
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def transcribe_audio(wav_path: str) -> str:
    try:
        with open(wav_path, "rb") as f:
            resp = await client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        return resp.text
    except Exception as e:
        print("❌ STT ERROR:", e)
        return ""
