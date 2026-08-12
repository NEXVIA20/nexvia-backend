from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import re

app = FastAPI(
    title="NEXVIA",
    version="0.5.3"
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):
    message: str


# ============================================================
# HELPER
# ============================================================

def contains_any(text: str, words: list[str]) -> bool:
    return any(word in text for word in words)


# ============================================================
# URL EXTRACTION
# ============================================================

def extract_urls(message: str):

    pattern = r"https?://[^\s]+|www\.[^\s]+"

    urls = re.findall(pattern, message)

    # Remove common punctuation accidentally captured
    cleaned_urls = []

    for url in urls:

        url = url.rstrip(".,!?;:)]}\"'")

        cleaned_urls.append(url)

    return list(dict.fromkeys(cleaned_urls))


# ============================================================
# INTENT ROUTER
# ============================================================

def detect_intent(message: str):

    text = message.lower().strip()

    # --------------------------------------------------------
    # EXPLICIT CHECK QUESTIONS
    # --------------------------------------------------------

    explicit_check_words = [
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

    if contains_any(text, explicit_check_words):
        return "CHECK", 0.95


    # --------------------------------------------------------
    # WARNING SIGNAL GROUPS
    # --------------------------------------------------------

    money_words = [
        "won",
        "winner",
        "prize",
        "reward",
        "lottery",
        "cash",
        "money",
        "refund",
        "claim",
        "bonus",
        "selected"
    ]

    urgency_words = [
        "urgent",
        "immediately",
        "immediate",
        "today",
        "now",
        "within 24 hours",
        "last warning",
        "final warning",
        "act now",
        "quickly"
    ]

    account_words = [
        "account",
        "bank account",
        "banking",
        "card",
        "kyc",
        "verification",
        "customer"
    ]

    threat_words = [
        "blocked",
        "block",
        "suspended",
        "suspend",
        "closed",
        "close",
        "deactivated",
        "deactivate",
        "expired",
        "freeze",
        "frozen",
        "will be stopped"
    ]

    sensitive_words = [
        "otp",
        "password",
        "pin",
        "cvv",
        "card number",
        "bank details",
        "account details",
        "login details"
    ]

    action_words = [
        "click",
        "open",
        "tap",
        "visit",
        "update",
        "verify",
        "confirm",
        "enter",
        "send",
        "share",
        "provide",
        "submit"
    ]


    # --------------------------------------------------------
    # URL
    # --------------------------------------------------------

    urls = extract_urls(message)

    has_url = len(urls) > 0


    # --------------------------------------------------------
    # SIGNAL COUNTS
    # --------------------------------------------------------

    money_signal = contains_any(text, money_words)
    urgency_signal = contains_any(text, urgency_words)
    account_signal = contains_any(text, account_words)
    threat_signal = contains_any(text, threat_words)
    sensitive_signal = contains_any(text, sensitive_words)
    action_signal = contains_any(text, action_words)


    # --------------------------------------------------------
    # CHECK DECISION
    # --------------------------------------------------------

    if sensitive_signal:
        return "CHECK", 0.93

    if has_url:
        return "CHECK", 0.93

    if account_signal and threat_signal:
        return "CHECK", 0.92

    if money_signal and urgency_signal:
        return "CHECK", 0.92

    if money_signal and action_signal:
        return "CHECK", 0.91

    if "kyc" in text and action_signal:
        return "CHECK", 0.92


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

    if contains_any(text, clear_words):
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

    if contains_any(text, compare_words):
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

    if contains_any(text, calculate_words):
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

    if contains_any(text, identify_words):
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

    if contains_any(text, prioritize_words):
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

    if contains_any(text, troubleshoot_words):
        return "TROUBLESHOOT", 0.91


    return "GENERAL", 0.60


# ============================================================
# CHECK 1.2 — MESSAGE ANALYSIS
# ============================================================

def analyse_check(message: str):

    text = message.lower()

    warnings = []

    urls = extract_urls(message)


    # --------------------------------------------------------
    # URGENCY
    # --------------------------------------------------------

    urgency_words = [
        "urgent",
        "immediately",
        "immediate",
        "today",
        "now",
        "within 24 hours",
        "last warning",
        "final warning",
        "act now",
        "quickly"
    ]

    if contains_any(text, urgency_words):

        warnings.append(
            "The message creates urgency or pressure to act quickly."
        )


    # --------------------------------------------------------
    # SENSITIVE INFORMATION
    # --------------------------------------------------------

    sensitive_words = [
        "otp",
        "password",
        "pin",
        "cvv",
        "card number",
        "bank details",
        "account details",
        "login details"
    ]

    if contains_any(text, sensitive_words):

        warnings.append(
            "The message asks for or mentions sensitive information such as OTP, PIN, password or banking details."
        )


    # --------------------------------------------------------
    # MONEY / PRIZE
    # --------------------------------------------------------

    money_words = [
        "won",
        "winner",
        "prize",
        "reward",
        "lottery",
        "cash prize",
        "free money",
        "refund",
        "bonus",
        "cash",
        "claim"
    ]

    if contains_any(text, money_words):

        warnings.append(
            "The message mentions money, a prize, reward, refund or unexpected benefit."
        )


    # --------------------------------------------------------
    # LINK
    # --------------------------------------------------------

    if urls:

        warnings.append(
            "The message contains a web link. Do not open it until the destination is verified."
        )


    # --------------------------------------------------------
    # ACCOUNT / KYC
    # --------------------------------------------------------

    account_words = [
        "account",
        "bank account",
        "banking",
        "kyc",
        "card"
    ]

    threat_words = [
        "blocked",
        "block",
        "suspended",
        "suspend",
        "closed",
        "deactivated",
        "expired",
        "freeze",
        "frozen"
    ]

    if contains_any(text, account_words) and contains_any(
        text,
        threat_words
    ):

        warnings.append(
            "The message suggests that an account, card or KYC status may be blocked, suspended, closed or expired."
        )


    # --------------------------------------------------------
    # ACTION REQUEST
    # --------------------------------------------------------

    action_words = [
        "click",
        "open",
        "tap",
        "visit",
        "update",
        "verify",
        "confirm",
        "enter",
        "send",
        "share",
        "provide",
        "submit"
    ]

    if contains_any(text, action_words):

        warnings.append(
            "The message asks you to take an immediate action."
        )


    # --------------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------------

    warnings = list(dict.fromkeys(warnings))


    # --------------------------------------------------------
    # RESULT LEVEL
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # ACTION
    # --------------------------------------------------------

    if warnings:

        action = (
            "Do not click unknown links or share OTP, PIN, "
            "password or banking information. "
            "If the message claims to be from a bank or government "
            "service, verify it through the organisation's official "
            "website or official phone number."
        )

    else:

        action = (
            "No immediate warning signs were detected, "
            "but this basic check cannot guarantee that a message "
            "is genuine."
        )


    # --------------------------------------------------------
    # URL INFORMATION
    # --------------------------------------------------------

    url_information = []

    for url in urls:

        url_information.append(
            "🔗 Link found: " + url
        )

    return {
        "level": level,
        "summary": summary,
        "warnings": warnings,
        "action": action,
        "urls": urls,
        "url_information": url_information
    }


# ============================================================
# RESPONSE GENERATOR
# ============================================================

def build_response(intent: str, message: str):

    if intent == "CHECK":

        result = analyse_check(message)

        response = result["summary"]

        if result["url_information"]:

            response += "\n\nLink detected:\n"

            for item in result["url_information"]:

                response += item + "\n"

            response += (
                "\nThis link has been detected, "
                "but NEXVIA has not yet verified its destination."
            )


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
