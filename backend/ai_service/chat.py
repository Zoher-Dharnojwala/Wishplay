def generate_reply(text, emotion, sentiment):
    if emotion == "joy":
        return "I'm so glad to hear that you’re feeling happy today!"
    elif emotion == "sadness":
        return "I can sense some sadness. Do you want to talk about what’s been weighing on your heart?"
    elif emotion == "anger":
        return "It sounds like something upset you. I’m here to listen if you’d like to share."
    elif emotion == "fear":
        return "It’s okay to feel worried sometimes. You’re safe here with me."
    else:
        return "Thank you for sharing. Tell me more about what’s been on your mind."
