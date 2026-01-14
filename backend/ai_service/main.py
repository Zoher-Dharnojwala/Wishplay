import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from ai_service.api.life_questions_api import router as history_router
load_dotenv()
print("ANTHROPIC_API_KEY loaded:", bool(os.getenv("ANTHROPIC_API_KEY")))
print("OPENAI_API_KEY loaded:", bool(os.getenv("OPENAI_API_KEY")))

app = FastAPI(
    title="Wishplay Mimir AI Service",
    description="Unified LLM backend (Anthropic Claude)",
    version="1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
AUDIO_STORAGE_PATH = os.path.join(os.path.dirname(__file__), "storage")
os.makedirs(AUDIO_STORAGE_PATH, exist_ok=True)
app.mount("/storage", StaticFiles(directory=AUDIO_STORAGE_PATH), name="storage")

# Routers
from ai_service.api.conversation_api import router as conversation_router
app.include_router(conversation_router)
app.include_router(history_router)
@app.get("/")
def root():
    return {"message": "Mimir AI running with Anthropic Claude only."}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    print("✅ Anthropic-only backend initialized")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "ai_service.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
