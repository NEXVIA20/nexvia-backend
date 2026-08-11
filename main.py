from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI(
    title="NEXVIA Core Engine",
    description="Step 2 & 3: Receiving and Understanding User Input",
    version="0.3.0"
)

# Step 2: Problem Input Schema
class ProblemRequest(BaseModel):
    user_problem: str

@app.get("/")
def home():
    return {
        "status": "online",
        "app": "NEXVIA",
        "tagline": "Keep your mind uncluttered.",
        "stage": "Step 2/3 - Active Listening Engaged"
    }

# STEP 2 & 3: Receive and Understand Input
@app.post("/chat/problem")
def process_problem(data: ProblemRequest):
    problem = data.user_problem
    
    # Simple rule-based understanding for Step 3 stub
    # (Next stage connects LLM / OpenAI for deep understanding)
    intent = "general_unburdening"
    if "stress" in problem.lower() or "overwhelmed" in problem.lower():
        intent = "emotional_decompress"
    elif "task" in problem.lower() or "work" in problem.lower() or "todo" in problem.lower():
        intent = "task_clarification"

    return {
        "status": "understood",
        "step_2_received_input": problem,
        "step_3_understanding": {
            "detected_intent": intent,
            "nexvia_acknowledgment": f"I understand your problem regarding: '{problem}'."
        },
        "next_step": "Step 4 - Skill selection pending model integration"
    }
