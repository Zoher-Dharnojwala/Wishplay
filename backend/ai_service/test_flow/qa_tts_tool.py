from crewai.tools import tool
import openai, tempfile

@tool
def qa_text_to_speech(text: str) -> str:
    """Convert text into spoken audio (MP3) and return file path."""
    response = openai.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    )
    output_path = tempfile.mktemp(suffix=".mp3")
    response.stream_to_file(output_path)
    return output_path
