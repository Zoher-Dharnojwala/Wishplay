from openai import AsyncOpenAI
client = AsyncOpenAI()

async def transcribe_bytes(wav_path):
    with open(wav_path, "rb") as f:
        wav_bytes = f.read()

    result = await client.audio.transcriptions.create(
        model="whisper-1",
        file=("audio.wav", wav_bytes, "audio/wav")
    )

    return result.text
