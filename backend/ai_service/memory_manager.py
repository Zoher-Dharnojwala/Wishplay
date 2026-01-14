import json
import os
import logging
from datetime import datetime


class MemoryManager:
    """
    A lightweight JSON-based conversation memory manager.
    Handles both short-term (per-user session) and long-term (global summary) memories.
    """

    def __init__(
        self,
        base_dir="/home/ubuntu/Mimir/ai_service/supermemory",
        memory_file="session_memory.json",
        global_file="memories.json",
        max_turns=5,
    ):
        # File paths
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

        self.memory_file = os.path.join(self.base_dir, memory_file)
        self.global_file = os.path.join(self.base_dir, global_file)
        self.max_turns = max_turns

        # Initialize memory data
        self.memory = self._load_json(self.memory_file, default={})
        self.memories = self._load_json(self.global_file, default=[])

    # =========================================================
    # 📥 INTERNAL HELPERS
    # =========================================================
    def _load_json(self, file_path, default):
        """Load JSON data safely with fallback."""
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logging.warning(f"⚠️ JSON decode error in {file_path}, resetting.")
                return default
        return default

    def _save_json(self, file_path, data):
        """Write JSON data safely."""
        try:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logging.error(f"❌ Failed to save JSON {file_path}: {e}")

    # =========================================================
    # 🧠 SESSION MEMORY (Per-User)
    # =========================================================
    def add_turn(self, user_id, user_message, ai_reply, emotion):
        """
        Save one conversational turn for a specific user.
        Keeps only the most recent N turns per user.
        """
        if not user_id:
            user_id = "anonymous"

        if user_id not in self.memory:
            self.memory[user_id] = []

        self.memory[user_id].append({
            "timestamp": datetime.utcnow().isoformat(),
            "user": user_message,
            "ai": ai_reply,
            "emotion": emotion,
        })

        # Keep only the latest N turns
        self.memory[user_id] = self.memory[user_id][-self.max_turns:]
        self._save_json(self.memory_file, self.memory)
        logging.info(f"💾 Saved memory turn for user {user_id}")

    def recall(self, user_id):
        """Retrieve the recent conversation turns for a user."""
        if not user_id:
            user_id = "anonymous"
        return self.memory.get(user_id, [])

    def clear_user_memory(self, user_id):
        """Clear memory for a specific user."""
        if user_id in self.memory:
            del self.memory[user_id]
            self._save_json(self.memory_file, self.memory)
            logging.info(f"🧹 Cleared memory for user {user_id}")

    # =========================================================
    # 🌍 GLOBAL MEMORY (Summaries, Emotional Snapshots)
    # =========================================================
    def add_memory(self, message: str, summary: str, emotion: str):
        """
        Append a summarized reflection or emotional insight to the global memory.
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "summary": summary,
            "emotion": emotion,
        }
        self.memories.append(entry)
        self._save_json(self.global_file, self.memories)
        logging.info("🧠 Added entry to global memory.")

    def get_all_memories(self):
        """Return all stored global memory entries."""
        return self.memories

    def clear_global_memories(self):
        """Wipe all long-term stored memories."""
        self.memories = []
        self._save_json(self.global_file, self.memories)
        logging.warning("⚠️ Global memories cleared.")
