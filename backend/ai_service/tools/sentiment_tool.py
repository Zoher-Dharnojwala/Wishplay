from ai_service.tools.base_tool import BaseTool
from transformers import pipeline


class SentimentTool(BaseTool):
    """
    Sentiment analysis using Hugging Face transformers.
    Compatible with your local BaseTool system.
    """

    name: str = "SentimentTool"
    description: str = "Analyzes sentiment of text (positive, neutral, negative)."

    def __init__(self):
        super().__init__()
        self.model = pipeline("sentiment-analysis")

    def _run(self, text: str) -> dict:
        try:
            results = self.model(text)
            label = results[0]["label"]
            score = float(results[0]["score"])
            return {"sentiment": label, "confidence": score}
        except Exception as e:
            return {"error": str(e)}
