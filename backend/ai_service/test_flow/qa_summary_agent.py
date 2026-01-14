from crewai import Agent

summary_agent = Agent(
    name="Voice Summarizer",
    role="Listener and context refiner",
    goal="Summarize the user's spoken response briefly and extract the main idea.",
    backstory="A neutral, concise assistant who distills meaning from speech.",
    llm="gpt-4o-mini"
)
