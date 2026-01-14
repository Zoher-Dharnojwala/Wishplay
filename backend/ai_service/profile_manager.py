# ai_service/profile_manager.py
import json
import os

PROFILE_FILE = "user_profiles.json"

# ---------- Utility Functions ----------

def _load_profiles():
    """Load all user profiles from disk."""
    if not os.path.exists(PROFILE_FILE):
        return {}
    with open(PROFILE_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def _save_profiles(profiles):
    """Save all profiles to disk."""
    with open(PROFILE_FILE, "w") as f:
        json.dump(profiles, f, indent=4)

# ---------- Public API ----------

def get_user_profile(user_id: str):
    """Fetch or initialize a user profile."""
    profiles = _load_profiles()
    if user_id not in profiles:
        profiles[user_id] = {
            "user_id": user_id,
            "preferred_tone": "empathetic",
            "conversation_pacing": "moderate",
            "topics_of_interest": [],
            "last_session_summary": "",
            "emotional_baseline": "neutral",
        }
        _save_profiles(profiles)
    return profiles[user_id]


def update_user_profile(user_id: str, updates: dict):
    """Update user profile with provided fields."""
    profiles = _load_profiles()
    profile = profiles.get(user_id, get_user_profile(user_id))
    profile.update(updates)
    profiles[user_id] = profile
    _save_profiles(profiles)
    return profile


def list_all_profiles():
    """List all stored user profiles."""
    return _load_profiles()

def add_reflection(user_id: str, reflection: dict):
    profiles = _load_profiles()
    profile = profiles.get(user_id, get_user_profile(user_id))

    if "reflections" not in profile:
        profile["reflections"] = []

    profile["reflections"].append(reflection)
    profile["reflections"] = profile["reflections"][-10:]  # keep last 10

    profiles[user_id] = profile
    _save_profiles(profiles)
    return profile

def update_emotional_baseline(user_id: str, new_emotion: str):
    profiles = _load_profiles()
    profile = profiles.get(user_id, get_user_profile(user_id))

    # Simple drift logic – can be upgraded later
    profile["emotional_baseline"] = new_emotion
    profiles[user_id] = profile
    _save_profiles(profiles)
    return profile
