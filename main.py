from fastapi import FastAPI, Query

app = FastAPI(
    title="NEXVIA Core Engine",
    description="Backend API supporting Type, Talk, Show, and Send input modes.",
    version="0.2.0"
)

@app.get("/")
def home():
    return {
        "status": "online",
        "app": "NEXVIA",
        "tagline": "Keep your mind uncluttered."
    }

# ⌨️ TYPE
@app.get("/chat/text")
def chat_text(message: str = Query(..., description="User text input")):
    return {
        "mode": "TYPE",
        "user_input": message,
        "nexvia_response": f"I hear you. Let's unburden your mind regarding: '{message}'."
    }

# 🎤 TALK
@app.get("/chat/voice")
def chat_voice():
    return {
        "mode": "TALK",
        "status": "Ready to accept audio stream/file."
    }

# 📷 SHOW
@app.get("/chat/vision")
def chat_vision():
    return {
        "mode": "SHOW",
        "status": "Ready to process images."
    }

# 🔗 SEND
@app.get("/chat/document")
def chat_document():
    return {
        "mode": "SEND",
        "status": "Ready to accept web links or documents."
    }
