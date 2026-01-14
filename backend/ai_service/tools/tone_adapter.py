import random

def adjust_tone(reply: str, tone: str, pacing: str, emotion: str) -> str:
    """
    Adjust the reply to sound emotionally aware, natural, and human-like.
    This version adds deep tonality, layered empathy, and random variation.
    """

    # --- Tone presets ---
    empathetic_starters = [
        "I can imagine how that must feel.",
        "It sounds like this means a lot to you.",
        "That must have been really emotional.",
        "I hear the care in your words.",
        "You’ve been carrying this for a while, haven’t you?",
        "That sounds deeply meaningful.",
        "Your openness really shows how much you cared.",
        "I can sense the emotion behind what you said."
    ]

    encouraging_starters = [
        "That’s incredible!",
        "I love hearing that!",
        "You should feel really proud of yourself.",
        "That’s such a powerful step forward.",
        "That’s wonderful progress!",
        "You’re truly making a difference for yourself.",
        "That kind of positivity is inspiring.",
        "I can tell how much effort you’ve put into this."
    ]

    calm_starters = [
        "Let's take a slow breath together.",
        "It’s okay to slow down and process this.",
        "We can go one thought at a time.",
        "You’re doing well by acknowledging this.",
        "Take a moment to just be here with me.",
        "Everything doesn’t need to be solved right now.",
        "You’re safe to share whatever you feel.",
        "We can move gently through this."
    ]

    reflective_starters = [
        "That’s a really thoughtful reflection.",
        "You’re seeing things in a very deep way.",
        "It’s interesting how you’ve connected that.",
        "You have such a clear way of expressing your thoughts.",
        "That’s a meaningful realization.",
        "You’ve given that a lot of consideration.",
        "It shows how much insight you have.",
        "That’s beautifully said."
    ]

    # --- Emotion layers ---
    sadness_layers = [
        "That sounds really heavy — thank you for trusting me with it.",
        "It’s okay to miss them and still move forward.",
        "Loss like that never fully fades, but it changes with time.",
        "It’s completely natural to feel that ache.",
        "I hear how much they meant to you.",
        "It’s hard when memories carry both love and pain.",
        "You’re allowed to sit with that sadness — it’s part of love.",
        "Sometimes healing means simply remembering with gentleness."
    ]

    joy_layers = [
        "That’s such a bright moment to celebrate!",
        "It’s wonderful to hear joy in your words.",
        "Moments like these deserve to be remembered.",
        "That happiness really shines through.",
        "You sound truly alive right now.",
        "That spark you feel — hold onto it.",
        "It’s great to see you in such good spirits!",
        "Your excitement is contagious!"
    ]

    anger_layers = [
        "It’s completely valid to feel frustrated.",
        "It sounds like something important wasn’t respected.",
        "You have every right to feel upset about that.",
        "Anger can be a sign that your values matter deeply.",
        "That must have felt unfair or painful.",
        "It’s okay to vent — you don’t have to bottle it up.",
        "I can tell this situation really affected you.",
        "Even strong emotions like this deserve to be heard."
    ]

    anxiety_layers = [
        "That sounds overwhelming — let’s slow it down together.",
        "You’re safe right here, right now.",
        "It’s okay to feel uncertain; that’s a very human reaction.",
        "Let’s take this one small step at a time.",
        "Your feelings make sense given everything going on.",
        "It’s okay to not have all the answers immediately.",
        "You don’t have to face this all at once.",
        "Let’s ground ourselves before thinking of next steps."
    ]

    love_layers = [
        "That kind of connection is truly special.",
        "It’s beautiful that you hold such care for others.",
        "Love like that often leaves lasting warmth.",
        "You’re speaking from a place of deep affection.",
        "That memory radiates kindness and closeness.",
        "It’s moving to hear how much love is in your story.",
        "That kind of bond can carry us through hard times.",
        "It’s lovely to hear love expressed so sincerely."
    ]

    # --- Follow-up suggestions ---
    followups = [
        "Would you like to tell me more about that?",
        "What stands out most when you think about it?",
        "How do you feel about it now?",
        "What helps you through moments like this?",
        "Is there a particular memory that comes to mind?",
        "How would you like to build on that feeling?",
        "What do you think this experience has taught you?",
        "I’d love to hear more, if you’d like to share."
    ]

    # --- Select tone prefix ---
    tone_map = {
        "empathetic": empathetic_starters,
        "encouraging": encouraging_starters,
        "calm": calm_starters,
        "reflective": reflective_starters
    }

    tone_prefix = random.choice(tone_map.get(tone, [""])) if tone else ""

    # --- Select emotion layer ---
    emotion_map = {
        "sadness": sadness_layers,
        "grief": sadness_layers,
        "joy": joy_layers,
        "love": love_layers,
        "anger": anger_layers,
        "frustration": anger_layers,
        "anxiety": anxiety_layers,
        "fear": anxiety_layers
    }

    emotion_layer = random.choice(emotion_map.get(emotion, [""])) if emotion else ""

    # --- Pacing hints ---
    pacing_hint = ""
    if pacing == "slow":
        pacing_hint = random.choice([
            " Let’s take our time with this.",
            " There’s no rush — I’m here with you.",
            " We can go slowly, one step at a time."
        ])
    elif pacing == "fast":
        pacing_hint = random.choice([
            " That’s really interesting — tell me more!",
            " I’d love to hear more details!",
            " Keep going, this is fascinating!"
        ])

    # --- Build natural final output ---
    followup = random.choice(followups)
    components = [tone_prefix, emotion_layer, reply, pacing_hint, followup]
    return " ".join([part.strip() for part in components if part]).strip()
