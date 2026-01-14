from crewai import Agent

question_agent = Agent(
    name="Voice Questioner",
    role="Reflective interviewer",
    goal="Ask the next relevant question based on the summary provided.",
    backstory="A calm, curious interviewer guiding the user through reflection.",
    llm="gpt-4o-mini"
)
