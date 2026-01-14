from ai_service.tools.base_tool import BaseTool
from transformers import pipeline


class EmotionTool(BaseTool):
    """
    A BaseTool-based emotion detector using the DistilRoBERTa model.
    """

    name = "emotion_detector"
    description = "Analyzes the emotional tone of a text input and returns dominant emotion with confidence."

    def _run(self, text: str) -> dict:
        """Analyze emotion from text and return results."""
        if not text or not text.strip():
            return {"error": "Text input missing."}

        try:
            model = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                top_k=None
            )

            results = model(text)
            emotions = {r["label"]: float(r["score"]) for r in results[0]}
            dominant = max(emotions, key=emotions.get)

            return {
                "dominant_emotion": dominant,
                "all_scores": emotions
            }

        except Exception as e:
            return {"error": str(e)}
