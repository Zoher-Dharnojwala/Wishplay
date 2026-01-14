import os
import base64
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VOICE = "alloy"

# -------------------------
# FIXED FULL TTS
# -------------------------
async def synthesize_speech(text: str) -> str:
    try:
        resp = await client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice=VOICE,
            input=text
        )

        # resp is the binary audio data
        audio_bytes = resp  # DO NOT resp.read(), do NOT await again

        # convert to base64
        return base64.b64encode(audio_bytes).decode()

    except Exception as e:
        print("❌ TTS FULL ERROR:", e)
        return None
async def synthesize_speech_stream(text: str):
    try:
        async with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice=VOICE,
            input=text
        ) as resp:

            async for chunk in resp.iter_bytes():
                yield base64.b64encode(chunk).decode()

    except Exception as e:
        print("❌ STREAM TTS ERROR:", e)
