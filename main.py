from fastapi import FastAPI

app = FastAPI(title="NEXVIA AI Core")

@app.get("/")
def home():
    return {"message": "Hello! I am NEXVIA."}
