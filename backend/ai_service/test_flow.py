import requests

samples = [
    "I'm so happy today!",
    "I'm really upset about what happened.",
    "I'm feeling fine, nothing special."
]

for msg in samples:
    res = requests.post("http://127.0.0.1:8000/chat", json={"message": msg})
    print(res.json())
