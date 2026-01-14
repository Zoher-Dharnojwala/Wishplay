from crewai import Agent

qa_agent = Agent(
    name="Simple QA Agent",
    role="Answer questions clearly and briefly.",
    goal="Provide direct answers to user questions without emotion or sentiment.",
    backstory="You are a straightforward assistant that only answers what is asked.",
    llm="gpt-4o-mini"
)
