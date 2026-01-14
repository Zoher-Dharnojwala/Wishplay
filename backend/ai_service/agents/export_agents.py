| **`tools/storage_tool.py`** | Wrapper around your `memory_manager` to save data. | ```python
from crewai import Tool
from memory.memory_manager import save_to_supermemory

class StorageTool(Tool):
    name = "Storage Tool"
    description = "Saves conversation data into long-term storage."

    def run(self, session_id, data):
        return save_to_supermemory(session_id, data)
``` |
| **`config/settings.py`** | Centralize API keys and settings. | ```python
import os
from dotenv import load_dotenv
load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
ELEVENLABS_KEY = os.getenv("ELEVENLABS_KEY")
``` |
| **`flows/life_reflection_flow.py`** | Master flow orchestrating all sections. | (I’ll generate full code when we migrate About You fully — see next step.) |
| **`main.py`** | FastAPI app + CrewAI bootloader. | ```python
from fastapi import FastAPI
from flows.life_reflection_flow import LifeReflectionFlow

app = FastAPI()

@app.post("/start-session")
def start_session():
    flow = LifeReflectionFlow()
    result = flow.kickoff()
    return result
``` |

---

## 🔄 3. What to **Rename / Move**

| Action | File |
|---------|------|
| Rename `api.py` → `main.py` |
| Move `emotion.py`, `sentiment.py`, `stt.py`, `tts_service.py`, `tone_adapter.py` into `/tools/` |
| Move `memory_manager.py` into `/memory/` folder |
| Move `supermemory/` into `/memory/supermemory.py` (or keep as folder) |
| Move all flow-like files (`about_you_voice_flow.py`, `screening_voice_flow.py`) into `/flows/` |
| Keep `knowledge/` and `audio/` folders as is (they are data sources). |

---

## 🚦 4. What You’ll Have After Migration

