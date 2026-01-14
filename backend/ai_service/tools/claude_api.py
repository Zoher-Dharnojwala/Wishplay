import os
from anthropic import AsyncAnthropic

client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

async def claude_api_call(prompt: str):
    response = await client.messages.create(
        model="claude-3-haiku-20240307",   # <-- This WILL work
        max_tokens=300,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.content[0].text
