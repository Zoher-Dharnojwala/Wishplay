from ai_service.tools.sentiment_tool import SentimentTool

# Initialize once when the module loads
_sentiment_tool = SentimentTool()

def analyze_sentiment(text: str):
    """
    Wrapper for SentimentTool to provide a simple interface.
    This is imported by screening_voice_flow.
    """
    result = _sentiment_tool._run(text)
    if "error" in result:
        return {"sentiment": "unknown", "confidence": 0.0, "error": result["error"]}
    return result
