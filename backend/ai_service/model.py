from transformers import pipeline
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from textblob import TextBlob
import logging
import torch

device= "cpu"

# --------------------------------------------------------
# Logging Setup
# --------------------------------------------------------
logging.basicConfig(
    filename="ai_service.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --------------------------------------------------------
# 1. Sentiment Analysis
# --------------------------------------------------------
try:
    sentiment_model = pipeline("text-classification",
                           model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
                           device=-1)
    logging.info("✅ Sentiment model loaded successfully.")
except Exception as e:
    logging.error(f"❌ Error loading sentiment model: {e}")
    sentiment_model = None


def analyze_text(text: str):
    if not text or not sentiment_model:
        return {"label": "neutral", "score": 0.0}

    result = sentiment_model(text)[0]
    return {
        "label": result["label"],
        "score": round(float(result["score"]), 4)
    }


# --------------------------------------------------------
# 2. Emotion Detection
# --------------------------------------------------------
try:
    emotion_model = pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        return_all_scores=True,
        device=-1 #force CPU
    )
    logging.info("✅ Emotion model loaded successfully.")
except Exception as e:
    logging.error(f"❌ Error loading emotion model: {e}")
    emotion_model = None


def analyze_emotion(text: str):
    if not text or not emotion_model:
        return {"emotions": []}

    results = emotion_model(text)[0]
    sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)
    top_emotions = [{r["label"]: round(float(r["score"]), 4)} for r in sorted_results[:3]]
    return {"emotions": top_emotions}


# --------------------------------------------------------
# 3. Summarization (Conversation-Optimized)
# --------------------------------------------------------
try:
    summarizer = pipeline(
        "summarization",
        model="philschmid/bart-large-cnn-samsum",
        tokenizer="philschmid/bart-large-cnn-samsum",
        device=-1 #force CPU
    )
    logging.info("✅ Conversation-optimized summarizer loaded successfully.")
except Exception as e:
    logging.error(f"❌ Error loading summarizer: {e}")
    summarizer = None


def summarize_text(text: str):
    """
    Generate a short conversational summary with confidence score.
    """
    if not text or not summarizer:
        return {"summary": "", "confidence": 0.0}

    # Skip summarization for short text
    if len(text.split()) < 20:
        return {"summary": text, "confidence": 1.0}

    try:
        result = summarizer(
            text,
            max_length=60,
            min_length=15,
            do_sample=True,
            temperature=0.8,
            top_p=0.9
        )

        summary = result[0]["summary_text"].strip()
        confidence = round(min(len(summary.split()) / len(text.split()), 1.0), 3)

        return {
            "summary": summary,
            "confidence": confidence
        }

    except Exception as e:
        logging.error(f"❌ Summarization failed: {e}")
        return {"summary": "", "confidence": 0.0}


# --------------------------------------------------------
# 4. Keyword Extraction
# --------------------------------------------------------
try:
    kw_model = KeyBERT(model=SentenceTransformer("all-MiniLM-L12-v2"))
    logging.info("✅ Keyword model loaded successfully.")
except Exception as e:
    logging.error(f"❌ Error loading KeyBERT model: {e}")
    kw_model = None


def extract_keywords(text: str):
    if not text or not kw_model:
        return {"keywords": []}

    try:
        keywords = kw_model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 2),
            stop_words="english",
            top_n=5,
            use_mmr=True,
            diversity=0.8
        )

        unique_keywords = []
        for kw, _ in keywords:
            clean_kw = kw.lower().strip()
            if all(clean_kw not in k for k in unique_keywords):
                unique_keywords.append(clean_kw)

        return {"keywords": [kw.capitalize() for kw in unique_keywords]}
    except Exception as e:
        logging.error(f"❌ Keyword extraction failed: {e}")
        return {"keywords": []}


# --------------------------------------------------------
# 5. NLP Handler (Adaptive Chat + Sentiment + Emotion)
# --------------------------------------------------------
class NLPHandler:
    def __init__(self):
        try:
            self.emotion_classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base"
            )
            logging.info("✅ NLPHandler emotion classifier initialized.")
        except Exception as e:
            logging.error(f"❌ Error initializing emotion classifier: {e}")
            self.emotion_classifier = None

    def process_message(self, text):
        if not text:
            return {"reply": "", "sentiment": "neutral", "emotion": "neutral"}

        sentiment = self.get_sentiment(text)
        emotion = self.detect_emotion(text)
        response = self.generate_reply(text)
        return {
            "reply": response,
            "sentiment": sentiment,
            "emotion": emotion
        }

    def get_sentiment(self, text):
        polarity = TextBlob(text).sentiment.polarity
        if polarity > 0.1:
            return "positive"
        elif polarity < -0.1:
            return "negative"
        else:
            return "neutral"

    def detect_emotion(self, text):
        if not self.emotion_classifier:
            return "unknown"
        try:
            result = self.emotion_classifier(text)
            return result[0]["label"]
        except Exception as e:
            logging.error(f"❌ Emotion detection failed: {e}")
            return "error"

    def generate_reply(self, text):
        sentiment = self.get_sentiment(text)
        if sentiment == "positive":
            return "I'm glad to hear that! Tell me more."
        elif sentiment == "negative":
            return "I'm sorry that you feel that way. Would you like to talk about it?"
        else:
            return "I see. Please continue."
