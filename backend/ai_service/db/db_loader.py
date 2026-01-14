import json
import random

class QuestionDB:
    def __init__(self, path="/wishplay/ai_service/knowledge/about_you_questions.json"):
        with open(path, "r") as f:
            self.data = json.load(f)
        self.questions = self.data["questions"]

    def get_question(self, emotion="neutral"):
        """
        Retrieve emotion-matching question.
        If none exists → fallback to neutral.
        """

        matches = [q for q in self.questions if q["emotion"] == emotion]

        if not matches:
            matches = [q for q in self.questions if q["emotion"] == "neutral"]

        return random.choice(matches)["text"]
