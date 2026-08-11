from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(
    title="NEXVIA",
    version="0.4.0"
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):
    message: str


# ============================================================
# NEXVIA INTENT ROUTER
# ============================================================

def detect_intent(message: str):

    text = message.lower().strip()

    # --------------------------------------------------------
    # CHECK
    # --------------------------------------------------------

    check_words = [
        "scam",
        "genuine",
        "fake",
        "fraud",
        "phishing",
        "suspicious",
        "verify",
        "real or fake",
        "is this genuine",
        "is this real"
    ]

    if any(word in text for word in check_words):
        return "CHECK", 0.95


    # --------------------------------------------------------
    # CLEAR / EXPLAIN
    # --------------------------------------------------------

    clear_words = [
        "what does this mean",
        "explain",
        "don't understand",
        "do not understand",
        "meaning",
        "confusing",
        "what is this",
        "explain this",
        "understand this"
    ]

    if any(word in text for word in clear_words):
        return "CLEAR", 0.94


    # --------------------------------------------------------
    # COMPARE
    # --------------------------------------------------------

    compare_words = [
        "which is better",
        "which one",
        "compare",
        "cheaper",
        "best one",
        "better one",
        "difference between",
        "should i buy",
        "which should i buy"
    ]

    if any(word in text for word in compare_words):
        return "COMPARE", 0.94


    # --------------------------------------------------------
    # CALCULATE
    # --------------------------------------------------------

    calculate_words = [
        "calculate",
        "how much",
        "average",
        "percentage",
        "percent",
        "total",
        "profit",
        "loss",
        "emi",
        "interest",
        "how many"
    ]

    if any(word in text for word in calculate_words):
        return "CALCULATE", 0.93


    # --------------------------------------------------------
    # IDENTIFY
    # --------------------------------------------------------

    identify_words = [
        "what is this",
        "identify",
        "what device",
        "what product",
        "what item",
        "name this"
    ]

    if any(word in text for word in identify_words):
        return "IDENTIFY", 0.92


    # --------------------------------------------------------
    # PRIORITIZE
    # --------------------------------------------------------

    prioritize_words = [
        "too many tasks",
        "where to start",
        "what should i do first",
        "prioritize",
        "priority",
        "organize my tasks",
        "too much work"
    ]

    if any(word in text for word in prioritize_words):
        return "PRIORITIZE", 0.92


    # --------------------------------------------------------
    # TROUBLESHOOT
    # --------------------------------------------------------

    troubleshoot_words = [
        "not working",
        "doesn't work",
        "does not work",
        "how do i fix",
        "fix this",
        "problem with",
        "error",
        "broken"
    ]

    if any(word in text for word in troubleshoot_words):
        return "TROUBLESHOOT", 0.91


    # --------------------------------------------------------
    # DEFAULT
    # --------------------------------------------------------

    return "GENERAL", 0.60


# ============================================================
# NEXVIA RESPONSE GENERATOR
# ============================================================

def build_response(intent: str, message: str):

    responses = {

        "CHECK":
            "I can check this for you. I will identify what needs to be verified and look for supporting information.",

        "CLEAR":
            "I can explain this in simple language and tell you what it means and what you may need to do.",

        "COMPARE":
            "I can compare the options and help you understand the important differences.",

        "CALCULATE":
            "I can calculate this for you and give you the result in a simple format.",

        "IDENTIFY":
            "I can help identify what you are looking at and explain what it is used for.",

        "PRIORITIZE":
            "Let's organize the problem and decide what you should deal with first.",

        "TROUBLESHOOT":
            "Let's identify what is causing the problem and work through the possible solution.",

        "GENERAL":
            "I understand that you need help. I will work out what kind of problem this is and guide you from there."
    }

    return responses.get(
        intent,
        responses["GENERAL"]
    )


# ============================================================
# NEXVIA HOME SCREEN
# ============================================================

@app.get("/")
def home():

    return FileResponse("index.html")


# ============================================================
# TEXT CHAT
# ============================================================

@app.get("/chat/text")
def chat_text(message: str):

    intent, confidence = detect_intent(message)

    return {
        "mode": "TYPE",
        "user_input": message,
        "intent": intent,
        "confidence": confidence,
        "nexvia_response": build_response(
            intent,
            message
        )
    }


# ============================================================
# CHAT POST ENDPOINT
# ============================================================

@app.post("/chat")
def chat(request: ChatRequest):

    intent, confidence = detect_intent(request.message)

    return {
        "mode": "TYPE",
        "user_input": request.message,
        "intent": intent,
        "confidence": confidence,
        "nexvia_response": build_response(
            intent,
            request.message
        )
    }
