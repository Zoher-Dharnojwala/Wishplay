import requests

BASE_URL = "http://127.0.0.1:6000"

def test_sentiment():
    payload = {"text": "I am very happy today"}
    r = requests.post(f"{BASE_URL}/predict", json=payload)
    print("\n🟢 Sentiment Test")
    print("Status:", r.status_code)
    print("Response:", r.json())

def test_emotion():
    payload = {"text": "I feel anxious but also hopeful about the future"}
    r = requests.post(f"{BASE_URL}/emotion", json=payload)
    print("\n🟢 Emotion Test")
    print("Status:", r.status_code)
    print("Response:", r.json())

def test_summarize():
    long_text = (
        "I have lived a long life filled with challenges and blessings. "
        "My career taught me resilience, while my family gave me joy and purpose. "
        "Looking back, I realize the importance of kindness and patience."
    )
    payload = {"text": long_text}
    r = requests.post(f"{BASE_URL}/summarize", json=payload)
    print("\n🟢 Summarization Test")
    print("Status:", r.status_code)
    print("Response:", r.json())

def test_keywords():
    payload = {"text": "Family has always been important to me, I worked hard in my career, and my faith guided me."}
    r = requests.post(f"{BASE_URL}/keywords", json=payload)
    print("\n🟢 Keywords Test")
    print("Status:", r.status_code)
    print("Response:", r.json())

if __name__ == "__main__":
    test_sentiment()
    test_emotion()
    test_summarize()
    test_keywords()
