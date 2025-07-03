from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import uvicorn

load_dotenv()

from agent import run_agent

app = FastAPI()

# Enable CORS (for local dev + Streamlit frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    try:
        reply = run_agent(request.message)
        return {"response": reply}
    except Exception as e:
        return {"response": f"❌ Agent crashed: {str(e)}"}

# ✅ Launch entry point (Railway/Render reads PORT env var)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # fallback for local dev
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port)
