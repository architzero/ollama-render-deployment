# api_wrapper.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Ollama API Wrapper", version="1.0.0")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3.2:3b")

class ChatRequest(BaseModel):
    message: str
    model: str = DEFAULT_MODEL
    temperature: float = 0.7
    max_tokens: int = 500
    stream: bool = False

class ChatResponse(BaseModel):
    response: str
    model: str
    total_duration: int
    load_duration: int
    prompt_eval_count: int
    eval_count: int

@app.get("/")
async def root():
    return {"message": "Ollama API Wrapper is running"}

@app.get("/health")
async def health_check():
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return {
                "status": "healthy",
                "ollama_url": OLLAMA_BASE_URL,
                "available_models": [model["name"] for model in models]
            }
        else:
            return {"status": "unhealthy", "error": "Ollama not responding"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "down", "error": str(e)}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        ollama_payload = {
            "model": request.model,
            "prompt": request.message,
            "stream": request.stream,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens
            }
        }

        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=ollama_payload,
            timeout=120
        )

        if response.status_code == 200:
            result = response.json()
            return ChatResponse(
                response=result["response"],
                model=request.model,
                total_duration=result.get("total_duration", 0),
                load_duration=result.get("load_duration", 0),
                prompt_eval_count=result.get("prompt_eval_count", 0),
                eval_count=result.get("eval_count", 0)
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Ollama API error: {response.text}"
            )

    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Request timeout")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Cannot connect to Ollama")
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models")
async def list_models():
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=500, detail="Failed to fetch models")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
