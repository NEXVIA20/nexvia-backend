from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="NEXVIA Core Engine",
    description="Step 3: Dynamic Intent Router & Problem Understanding",
    version="0.3.5"
)

# 1. Structured Understanding Schema (NEXVIA Internal Representation)
class IntentUnderstanding(BaseModel):
    primary_intent: str
    core_problem: str
    action_needed: str
    response_mode: List[str]

# 2. Output Response Object
class RouterResponse(BaseModel):
    status: str
    user_input: str
    understanding: IntentUnderstanding
    nexvia_intervention: str

# 3. Intent Router Function (Extracts context -> Map to action)
def analyze_intent(user_input: str) -> IntentUnderstanding:
    text = user_input.lower()
    
    # Priority Routing Logic (Engine-ready for LLM replacement)
    if any(w in text for w in ["task", "todo", "start", "overwhelmed", "prioritize", "busy"]):
        return IntentUnderstanding(
            primary_intent="PRIORITIZE",
            core_problem="Overwhelmed by task volume or decision paralysis",
            action_needed="Guide user to dump tasks via Type, Talk, or Show",
            response_mode=["TEXT", "VOICE"]
        )
    elif any(w in text for w in ["scam", "sms", "link", "real", "fake", "genuine"]):
        return IntentUnderstanding(
            primary_intent="CHECK_SECURITY",
            core_problem="Uncertainty about message authenticity",
            action_needed="Analyze link or text structure for scam indicators",
            response_mode=["TEXT"]
        )
    elif any(w in text for w in ["compare", "better", "choose", "versus", "vs"]):
        return IntentUnderstanding(
            primary_intent="COMPARE",
            core_problem="Evaluating multiple options for a decision",
            action_needed="Provide pros/cons breakdown and recommendation",
            response_mode=["TEXT"]
        )
    else:
        return IntentUnderstanding(
            primary_intent="UNBURDEN_GENERAL",
            core_problem="General clutter or mental unburdening request",
            action_needed="Provide active listening and request clarifying details",
            response_mode=["TEXT", "VOICE"]
        )

# 4. Main Input Route: Receive -> Understand -> Classify -> Respond
@app.get("/chat/text", response_model=RouterResponse)
def chat_text(message: str = Query(..., description="User raw input")):
    # STEP 3: Pass raw input into the Router
    understanding = analyze_intent(message)
    
    # Intervention Crafting based on Intent
    if understanding.primary_intent == "PRIORITIZE":
        intervention = "Let's sort them out. Send me your tasks — you can type them, speak them, or take a photo. I'll help you decide what to do first."
    elif understanding.primary_intent == "CHECK_SECURITY":
        intervention = "Paste the message or send a screenshot of the link here. I'll analyze it for red flags right now."
    elif understanding.primary_intent == "COMPARE":
        intervention = "Tell me or show me the options you're weighing. I'll break down the key differences for you."
    else:
        intervention = f"I'm listening. Tell me more about what's on your mind regarding: '{message}'."

    return RouterResponse(
        status="understood",
        user_input=message,
        understanding=understanding,
        nexvia_intervention=intervention
    )

@app.get("/")
def home():
    return {
        "status": "online",
        "engine": "NEXVIA Core 0.3.5",
        "stage": "Step 3 - Intent Router Active"
    }
