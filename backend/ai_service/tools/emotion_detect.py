from openai import AsyncOpenAI
client = AsyncOpenAI()

async def detect_emotion(text: str) -> str:
    """
    Returns: "positive", "neutral", "sad", "angry", "fear", "anxious"
    """

    prompt = f"""
Classify the user's emotion from this message:
"{text}"

Return ONE WORD:
positive, neutral, sad, angry, anxious, fear.
"""

    res = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=3,
        temperature=0
    )

    emo = res.choices[0].message.content.strip().lower()
    return emo if emo in ["positive","neutral","sad","angry","anxious","fear"] else "neutral"


