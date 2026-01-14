import os
import subprocess
import logging
import whisper
from ai_service.tools.base_tool import BaseTool


logging.basicConfig(level=logging.INFO)


class SpeechToTextTool(BaseTool):
    """
    CrewAI Tool wrapper for Whisper speech-to-text transcription.
    Converts any audio file to 16kHz mono WAV and transcribes to text.
    """

    name = "SpeechToTextTool"
    description = "Converts speech audio to text using OpenAI Whisper (base model)."

    def __init__(self):
        super().__init__()
        try:
            self.model = whisper.load_model("base")
            logging.info("✅ Whisper model loaded successfully (CrewAI tool).")
        except Exception as e:
            self.model = None
            logging.error(f"❌ Failed to load Whisper model: {e}")

    def run(self, file_path: str):
        """
        Transcribe the given audio file into text.
        Args:
            file_path: Path to the input audio file.
        Returns:
            dict: { 'text': str, 'language': str } or { 'error': str }
        """
        if not self.model:
            return {"error": "Whisper model not loaded"}

        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        temp_wav = f"{os.path.splitext(file_path)[0]}_converted.wav"

        try:
            # Convert input to mono 16kHz WAV
            logging.info(f"🎧 Converting {file_path} → {temp_wav}")
            result = subprocess.run(
                ["ffmpeg", "-y", "-i", file_path, "-ar", "16000", "-ac", "1", temp_wav],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            if result.returncode != 0:
                logging.error(f"FFmpeg conversion failed:\n{result.stderr.decode()}")
                return {"error": "Audio conversion failed"}

            # Run Whisper transcription
            logging.info(f"🧠 Running Whisper transcription on {temp_wav}")
            result = self.model.transcribe(temp_wav, fp16=False, language="en")
            text = result.get("text", "").strip()
            lang = result.get("language", "en")

            os.remove(temp_wav)
            logging.info(f"✅ Transcription complete ({lang}): {text[:60]}...")
            return {"text": text, "language": lang}

        except Exception as e:
            logging.error(f"Transcription failed: {e}")
            return {"error": str(e)}
