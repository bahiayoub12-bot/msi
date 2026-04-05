import os
import uuid
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from g4f.client import Client

API_SECRET_KEY = os.getenv("API_SECRET_KEY", "change-secret-key-2026")

client = Client()

app = FastAPI(title="mse_ai_api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/v1/chat/completions")
async def chat(request: Request):
    authorization = request.headers.get("authorization", "")
    if authorization.replace("Bearer ", "").strip() != API_SECRET_KEY:
        return JSONResponse(status_code=401, content={"error": "Invalid API Key"})

    data = await request.json()
    messages = data.get("messages", [])

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        reply = response.choices[0].message.content
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:29]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "gpt-4o-mini",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": reply},
                "finish_reason": "stop"
            }]
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/")
async def health():
    return {"status": "running", "message": "mse_ai_api Server is active!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
