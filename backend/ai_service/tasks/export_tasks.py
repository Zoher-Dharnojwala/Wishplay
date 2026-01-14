from crewai import Task
from tools.storage_tool import StorageTool

storage_tool = StorageTool()

export_task = Task(
    description="Store conversation data into long-term memory after session end.",
    expected_output="Session transcript and emotions archived.",
    agent="memory_weaver"
)

def execute_export_task(user_id, data):
    storage_tool.run(user_id, data)
    return {"status": "Session saved"}
