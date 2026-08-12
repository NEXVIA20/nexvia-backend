from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import re

app = FastAPI(
    title="NEXVIA",
    version="0.5.1"
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):
    message: str


# ============================================================
# INTENT ROUTER
# ============================================================

def detect_intent(message: str):

    text = message.lower().strip()

    # --------------------------------------------------------
    # EXPLICIT CHECK QUESTIONS
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
        "is this real",
        "is this safe",
        "safe or not",
        "is this a scam"
    ]

    if any(word in text for word in check_words):
        return "CHECK", 0.95


    # --------------------------------------------------------
    # CHECK BY MESSAGE CONTENT
    # --------------------------------------------------------
    # A user may simply paste a suspicious message without
    # asking "is this a scam?"

    suspicious_content_words = [
        "account will be blocked",
        "account will be suspended",
        "account blocked",
        "account suspended",
        "kyc expired",
        "kyc update",
        "verify your account",
        "verify immediately",
        "click this link",
        "click the link",
        "click here",
        "act immediately",
        "act now",
        "urgent",
        "immediately",
        "last warning",
        "final warning",
        "send otp",
        "share otp",
        "enter otp",
        "provide otp",
        "share your password",
        "enter your password",
        "share pin",
        "enter pin",
        "card will be blocked",
        "you have won",
        "you won",
        "winner",
        "lottery",
        "cash prize",
        "claim your prize",
        "claim reward",
        "free money",
        "refund"
    ]

    suspicious_matches = sum(
        1 for word in suspicious_content_words
        if word in text
    )

    has_url = bool(
        re.search(
            r"https?://[^\s]+|www\.[^\s]+",
            text
        )
    )

    if suspicious_matches >= 1 or has_url:
        return "CHECK", 0.90


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
    # GENERAL
    # --------------------------------------------------------

    return "GENERAL", 0.60


# ============================================================
# CHECK 1.0 — BASIC MESSAGE ANALYSIS
# ============================================================

def analyse_check(message: str):

    text = message.lower()

    warnings = []


    # URGENCY

    urgency_words = [
        "urgent",
        "immediately",
        "immediate",
        "today",
        "now",
        "within 24 hours",
        "last warning",
        "final warning",
        "act now"
    ]

    if any(word in text for word in urgency_words):

        warnings.append(
            "The message uses urgent or threatening language."
        )


    # OTP / PASSWORD / PIN

    sensitive_words = [
        "otp",
        "password",
        "pin",
        "cvv",
        "card number",
        "bank details",
        "account details"
    ]

    if any(word in text for word in sensitive_words):

        warnings.append(
            "The message asks for or mentions sensitive information such as OTP, PIN, password or banking details."
        )


    # MONEY / PRIZE

    money_words = [
        "you won",
        "winner",
        "lottery",
        "prize",
        "cash prize",
        "reward",
        "free money",
        "refund",
        "claim money"
    ]

    if any(word in text for word in money_words):

        warnings.append(
            "The message mentions an unexpected prize, reward, refund or money."
        )


    # LINK

    urls = re.findall(
        r"https?://[^\s]+|www\.[^\s]+",
        message
    )

    if urls:

        warnings.append(
            "The message contains a web link. Do not open it until the destination is verified."
        )


    # ACCOUNT / KYC

    account_words = [
        "account will be blocked",
        "account will be closed",
        "account suspended",
        "account blocked",
        "kyc expired",
        "kyc update",
        "verify your account"
    ]

    if any(word in text for word in account_words):

        warnings.append(
            "The message uses an account-blocking, KYC or verification warning."
        )


    # RESULT

    if len(warnings) >= 3:

        level = "HIGH"

        summary = (
            "⚠️ Several warning signs were found. "
            "Treat this message with caution."
        )

    elif len(warnings) >= 1:

        level = "MEDIUM"

        summary = (
            "⚠️ Some warning signs were found. "
            "Be careful before taking any action."
        )

    else:

        level = "LOW"

        summary = (
            "No obvious warning signs were detected "
            "by this basic check."
        )


    # ACTION

    if warnings:

        action = (
            "Do not click unknown links or share OTP, PIN, "
            "password or banking information. "
            "If the message claims to be from a bank or government "
            "service, verify it through the organisation's official website or phone number."
        )

    else:

        action = (
            "No immediate warning signs were detected, "
            "but this basic check cannot guarantee that a message is genuine."
        )


    return {
        "level": level,
        "summary": summary,
        "warnings": warnings,
        "action": action
    }


# ============================================================
# RESPONSE GENERATOR
# ============================================================

def build_response(intent: str, message: str):

    if intent == "CHECK":

        result = analyse_check(message)

        response = result["summary"]

        if result["warnings"]:

            response += "\n\nWhy:\n"

            for warning in result["warnings"]:

                response += "• " + warning + "\n"

        response += "\nWhat should I do?\n"
        response += result["action"]

        return response


    responses = {

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
# HOME
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
# POST CHAT
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
