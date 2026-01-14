import base64
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ----------------------------------
# NON-STREAMING TTS (FULL AUDIO)
# ----------------------------------
async def tts_full(text: str) -> str:
    try:
        resp = await client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=text
        )

        # YOUR SDK returns HttpxBinaryResponseContent
        # So .read() is SYNC — do NOT await.
        audio_bytes = resp.read()

        return base64.b64encode(audio_bytes).decode()

    except Exception as e:
        print("❌ TTS FULL ERROR:", e)
        return None


# ----------------------------------
# STREAMING TTS (PCM chunks)
# ----------------------------------
async def tts_stream(text: str):
    try:
        async with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=text
        ) as r:
            async for chunk in r.iter_bytes():
                if chunk:
                    yield base64.b64encode(chunk).decode()

    except Exception as e:
        print("❌ STREAM TTS ERROR:", e)
        return
