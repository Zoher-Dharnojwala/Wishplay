from ai_service.tools.emotion_tool import EmotionTool

# Initialize once at import
_emotion_tool = EmotionTool()

def get_emotion(text: str):
    """
    Wrapper for EmotionTool to keep backward compatibility.
    This is what screening_voice_flow imports.
    """
    result = _emotion_tool._run(text)
    if "error" in result:
        return {"dominant_emotion": "unknown", "error": result["error"]}
    return result
