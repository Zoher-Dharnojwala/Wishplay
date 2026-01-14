from faster_whisper import WhisperModel
import asyncio

# Load model only ONCE (this is good)
model = WhisperModel("base", device="cpu", compute_type="int8")

async def transcribe_pcm(pcm_bytes: bytes) -> str:
    result = await client.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe",
        file=("audio.wav", pcm_bytes, "audio/wav")
    )
    return result.text

