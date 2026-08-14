from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import re
from urllib.parse import urlparse

app = FastAPI(
    title="NEXVIA",
    version="0.6.0"
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

    cleaned_urls = []

    for url in urls:
        url = url.rstrip(".,!?;:)]}\"'")
        cleaned_urls.append(url)

    return list(dict.fromkeys(cleaned_urls))


# ============================================================
# URL STRUCTURE ANALYSIS
# ============================================================

def analyse_url_structure(url: str):

    original_url = url

    if url.startswith("www."):
        parsed = urlparse("https://" + url)
    else:
        parsed = urlparse(url)

    domain = parsed.netloc.lower()

    if "@" in domain:
        domain = domain.split("@")[-1]

    domain = domain.split(":")[0]

    scheme = parsed.scheme.lower()

    signals = []

    caution_words = [
        "login",
        "signin",
        "verify",
        "verification",
        "secure",
        "security",
        "account",
        "bank",
        "banking",
        "wallet",
        "payment",
        "support",
        "update",
        "confirm"
    ]

    domain_parts = re.split(r"[-.]", domain)

    found_words = []

    for word in caution_words:
        if word in domain_parts:
            found_words.append(word)

    if found_words:
        signals.append(
            "The domain contains terms commonly associated with "
            "login, verification, banking or account activity: "
            + ", ".join(found_words) + "."
        )

    if "@" in original_url:
        signals.append(
            "The URL contains an '@' character, which can be used "
            "to disguise the actual destination."
        )

    if len(domain) > 50:
        signals.append(
            "The domain name is unusually long."
        )

    if domain.count("-") >= 3:
        signals.append(
            "The domain contains several hyphens, which can sometimes "
            "be seen in impersonation-style domains."
        )

    if scheme == "http":
        signals.append(
            "The link does not use HTTPS."
        )

    return {
        "url": original_url,
        "domain": domain,
        "scheme": scheme,
        "signals": list(dict.fromkeys(signals))
    }


# ============================================================
# CALCULATOR ENGINE — NEXVIA 0.6.0
# ============================================================

def format_number(number):

    if float(number).is_integer():
        return str(int(number))

    return f"{number:.10f}".rstrip("0").rstrip(".")


def calculate_expression(message: str):

    text = message.lower().strip()

    # --------------------------------------------------------
    # PERCENTAGE
    # Example: 25% of 800
    # --------------------------------------------------------

    percentage_pattern = (
        r"(\d+(?:\.\d+)?)\s*"
        r"(?:%|percent|percentage)\s*"
        r"of\s*"
        r"(\d+(?:\.\d+)?)"
    )

    percentage_match = re.search(
        percentage_pattern,
        text
    )

    if percentage_match:

        percentage = float(
            percentage_match.group(1)
        )

        number = float(
            percentage_match.group(2)
        )

        result = (percentage / 100) * number

        return (
            f"{format_number(percentage)}% of "
            f"{format_number(number)} = "
            f"{format_number(result)}"
        )

    # --------------------------------------------------------
    # BASIC ARITHMETIC
    # --------------------------------------------------------

    expression = text

    expression = re.sub(
        r"^(calculate|compute|what is)\s+",
        "",
        expression
    )

    expression = expression.replace("×", "*")
    expression = expression.replace("÷", "/")

    expression = re.sub(
        r"\bplus\b",
        "+",
        expression
    )

    expression = re.sub(
        r"\bminus\b",
        "-",
        expression
    )

    expression = re.sub(
        r"\btimes\b",
        "*",
        expression
    )

    expression = re.sub(
        r"\bdivided by\b",
        "/",
        expression
    )

    match = re.fullmatch(
        r"\s*(\d+(?:\.\d+)?)\s*"
        r"([+\-*/])\s*"
        r"(\d+(?:\.\d+)?)\s*",
        expression
    )

    if not match:
        return None

    first = float(match.group(1))
    operator = match.group(2)
    second = float(match.group(3))

    if operator == "+":
        result = first + second

    elif operator == "-":
        result = first - second

    elif operator == "*":
        result = first * second

    elif operator == "/":

        if second == 0:
            return "I cannot divide by zero."

        result = first / second

    return (
        f"{format_number(first)} "
        f"{operator} "
        f"{format_number(second)} = "
        f"{format_number(result)}"
    )


# ============================================================
# INTENT ROUTER
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
        "is this real",
        "is this safe",
        "safe or not",
        "is this a scam"
    ]

    if contains_any(text, check_words):
        return "CHECK", 0.95

    # --------------------------------------------------------
    # SECURITY SIGNALS
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

    urls = extract_urls(message)

    if contains_any(text, sensitive_words):
        return "CHECK", 0.93

    if urls:
        return "CHECK", 0.93

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
        "verification"
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

    money_words = [
        "won",
        "winner",
        "prize",
        "reward",
        "lottery",
        "cash",
        "money",
        "refund",
        "bonus",
        "claim"
    ]

    if (
        contains_any(text, account_words)
        and contains_any(text, threat_words)
    ):
        return "CHECK", 0.92

    if (
        contains_any(text, money_words)
        and contains_any(text, urgency_words)
    ):
        return "CHECK", 0.92

    if (
        contains_any(text, money_words)
        and contains_any(text, action_words)
    ):
        return "CHECK", 0.91

    # --------------------------------------------------------
    # CLEAR
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
        "how many",
        "compute"
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

    # --------------------------------------------------------
    # GENERAL
    # --------------------------------------------------------

    return "GENERAL", 0.60


# ============================================================
# CHECK ANALYSIS
# ============================================================

def analyse_check(message: str):

    text = message.lower()

    warnings = []

    urls = extract_urls(message)

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

    if contains_any(text, urgency_words):

        warnings.append(
            "The message creates urgency or pressure to act quickly."
        )

    if contains_any(text, sensitive_words):

        warnings.append(
            "The message asks for or mentions sensitive information "
            "such as OTP, PIN, password or banking details."
        )

    if contains_any(text, money_words):

        warnings.append(
            "The message mentions money, a prize, reward, refund "
            "or unexpected benefit."
        )

    if (
        contains_any(text, account_words)
        and contains_any(text, threat_words)
    ):

        warnings.append(
            "The message suggests that an account, card or KYC status "
            "may be blocked, suspended, closed or expired."
        )

    if contains_any(text, action_words):

        warnings.append(
            "The message asks you to take an immediate action."
        )

    warnings = list(dict.fromkeys(warnings))

    url_analysis = []

    for url in urls:
        url_analysis.append(
            analyse_url_structure(url)
        )

    total_warnings = len(warnings)

    for item in url_analysis:
        total_warnings += len(item["signals"])

    if total_warnings >= 3:

        summary = (
            "⚠️ Several warning signs were found. "
            "Treat this message with caution."
        )

    elif total_warnings >= 1:

        summary = (
            "⚠️ Some warning signs were found. "
            "Be careful before taking any action."
        )

    else:

        summary = (
            "No obvious warning signs were detected "
            "by this basic check."
        )

    if total_warnings > 0:

        action = (
            "Do not click unknown links or share OTP, PIN, "
            "password or banking information. If the message "
            "claims to be from a bank or government service, "
            "verify it through the organisation's official "
            "website or official phone number."
        )

    else:

        action = (
            "No immediate warning signs were detected, "
            "but this basic check cannot guarantee that a "
            "message is genuine."
        )

    return {
        "summary": summary,
        "warnings": warnings,
        "url_analysis": url_analysis,
        "action": action
    }


# ============================================================
# RESPONSE GENERATOR
# ============================================================

def build_response(intent: str, message: str):

    # --------------------------------------------------------
    # CHECK
    # --------------------------------------------------------

    if intent == "CHECK":

        result = analyse_check(message)

        response = result["summary"]

        if result["url_analysis"]:

            response += "\n\n🔗 Link detected:"

            for item in result["url_analysis"]:

                response += (
                    "\nURL: " + item["url"]
                )

                response += (
                    "\nDomain: " + item["domain"]
                )

                if item["scheme"] == "https":
                    response += "\nHTTPS: Yes"

                elif item["scheme"] == "http":
                    response += "\nHTTPS: No"

                if item["signals"]:

                    response += (
                        "\n\n⚠️ URL structure signals:"
                    )

                    for signal in item["signals"]:

                        response += (
                            "\n• " + signal
                        )

                else:

                    response += (
                        "\n\nNo suspicious indicators were "
                        "detected from the URL structure alone."
                    )

            response += (
                "\n\nImportant: This is only a basic URL "
                "inspection. It does not confirm that the "
                "website is trustworthy."
            )

        if result["warnings"]:

            response += "\n\nWhy:"

            for warning in result["warnings"]:

                response += "\n• " + warning

        response += "\n\nWhat should I do?\n"
        response += result["action"]

        return response

    # --------------------------------------------------------
    # CALCULATE
    # --------------------------------------------------------

    if intent == "CALCULATE":

        result = calculate_expression(message)

        if result:

            return (
                "I calculated this for you.\n\n"
                + result
            )

        return (
            "I can calculate this for you, but I need "
            "a clearer calculation.\n\n"
            "Examples:\n"
            "• 25% of 800\n"
            "• 800 + 250\n"
            "• 800 - 250\n"
            "• 25 × 8\n"
            "• 800 ÷ 4"
        )

    # --------------------------------------------------------
    # OTHER INTENTS
    # --------------------------------------------------------

    responses = {

        "CLEAR":
            "I can explain this in simple language and tell you what it means and what you may need to do.",

        "COMPARE":
            "I can compare the options and help you understand the important differences.",

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
# GET CHAT
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

    intent, confidence = detect_intent(
        request.message
    )

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
