import logging
from ai_service.tools.base_tool import BaseTool
from ai_service.memory_manager import MemoryManager

# Initialize a shared memory manager instance
memory = MemoryManager()

class StorageTool(BaseTool):
    """
    CrewAI Tool for managing both user-specific and global conversation memory.
    Lets agents remember user turns, recall past context, and add summarized memories.
    """

    name = "StorageTool"
    description = (
        "Stores and retrieves conversational memory for each user, "
        "and manages global summaries and emotional states."
    )

    def run(self, action: str, **kwargs):
        """
        Run a memory action.

        Args:
            action (str): 'add_turn', 'recall', or 'add_memory'
            user_id (str, optional): ID of the user
            user_message (str, optional): The user's message
            ai_reply (str, optional): The AI's reply
            emotion (str, optional): Emotion label
            message (str, optional): Text for global memory
            summary (str, optional): Summary of a message
        """
        try:
            if action == "add_turn":
                user_id = kwargs.get("user_id", "anonymous")
                user_message = kwargs.get("user_message", "")
                ai_reply = kwargs.get("ai_reply", "")
                emotion = kwargs.get("emotion", "neutral")

                memory.add_turn(user_id, user_message, ai_reply, emotion)
                logging.info(f"💾 Memory turn added for {user_id}")
                return {"status": "ok", "action": "add_turn"}

            elif action == "recall":
                user_id = kwargs.get("user_id", "anonymous")
                context = memory.recall(user_id)
                logging.info(f"🧠 Retrieved memory for {user_id}: {len(context)} turns")
                return {"context": context}

            elif action == "add_memory":
                message = kwargs.get("message", "")
                summary = kwargs.get("summary", "")
                emotion = kwargs.get("emotion", "neutral")

                memory.add_memory(message, summary, emotion)
                logging.info("🌍 Added entry to global memory.")
                return {"status": "ok", "action": "add_memory"}

            else:
                return {"error": f"Unknown action: {action}"}

        except Exception as e:
            logging.error(f"❌ StorageTool error: {e}")
            return {"error": str(e)}
