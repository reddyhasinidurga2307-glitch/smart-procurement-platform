import json
import os
import sys


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FARMER_ACCESS_DIR = os.path.dirname(CURRENT_DIR)
CORE_DIR = os.path.join(FARMER_ACCESS_DIR, "core")

if CORE_DIR not in sys.path:
    sys.path.insert(0, CORE_DIR)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import google.generativeai as genai
    GEMINI_LIBRARY_AVAILABLE = True
except Exception:
    GEMINI_LIBRARY_AVAILABLE = False

from smart_parser import smart_parse_message


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

if GEMINI_LIBRARY_AVAILABLE and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        GEMINI_AVAILABLE = True
    except Exception:
        GEMINI_AVAILABLE = False
else:
    GEMINI_AVAILABLE = False


def understand_with_gemini(message):
    """
    Try Gemini first.
    If Gemini is unavailable, quota-limited, or fails,
    return None so the local Smart Parser can handle the request.
    """

    if not GEMINI_AVAILABLE:
        return None

    try:
        model = genai.GenerativeModel(GEMINI_MODEL)

        prompt = f"""
You are the understanding engine of GrainFlow Smart Procurement Platform.

Understand the farmer's message and return ONLY a simple JSON object.

Message:
{message}

Possible intents:
SELL_GRAIN
BUY_GRAIN
CHECK_STATUS
UPDATE_STATUS
GET_ALL_REQUESTS

For SELL_GRAIN or BUY_GRAIN extract:
farmer_name
product
quantity
location

For CHECK_STATUS extract:
request_id

For UPDATE_STATUS extract:
request_id
status

IMPORTANT:
Accept ANY agricultural or food product.
Examples:
tomatoes, apples, green apples, dragon fruit, mushrooms,
chillies, barley, rice, wheat, vegetables, fruits, etc.

Return:
{{
  "intent": "...",
  "details": {{
    "farmer_name": null,
    "buyer_name": null,
    "product": null,
    "quantity": null,
    "location": null,
    "request_id": null,
    "status": null
  }}
}}
"""

        response = model.generate_content(prompt)

        if not response or not response.text:
            return None

        text = response.text.strip()

        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "").strip()

        return json.loads(text)

    except Exception as error:
        print(f"GEMINI FALLBACK: {error}")
        return None


def understand_farmer_message(message, conversation_context=None):
    """
    Understand a farmer message.

    Returns a normalized internal structure:
        {"intent": "...", "details": {...}}

    Gemini is optional. Local Smart Parser is the reliable fallback.
    """

    if not message:
        return {
            "intent": None,
            "details": {}
        }

    try:
        gemini_result = understand_with_gemini(message)

        if gemini_result:
            return _normalize_parser_result(gemini_result)

    except Exception as error:
        print(f"GEMINI ERROR: {error}")

    try:
        local_result = smart_parse_message(message)

        if local_result:
            return _normalize_parser_result(local_result)

    except Exception as error:
        print(f"LOCAL PARSER ERROR: {error}")

    return {
        "intent": None,
        "details": {}
    }


def _normalize_parser_result(result):
    if not isinstance(result, dict):
        return {
            "intent": None,
            "details": {}
        }

    if isinstance(result.get("data"), dict):
        result = result["data"]

    intent = (
        result.get("intent")
        or result.get("action")
        or result.get("request_type")
    )

    details = result.get("details")

    if not isinstance(details, dict):
        details = {}

    for field in [
        "farmer_name",
        "buyer_name",
        "person_name",
        "grain_type",
        "commodity",
        "product",
        "quantity",
        "location",
        "request_id",
        "status",
    ]:
        if field in result and result[field] is not None:
            details.setdefault(field, result[field])

    person_name = details.pop("person_name", None)
    if person_name:
        if intent == "BUY_GRAIN":
            details.setdefault("buyer_name", person_name)
        else:
            details.setdefault("farmer_name", person_name)

    product = (
        details.pop("commodity", None)
        or details.pop("product", None)
    )
    if product and not details.get("grain_type"):
        details["grain_type"] = product

    return {
        "intent": intent,
        "details": details
    }


if __name__ == "__main__":
    print("Testing GrainFlow Understanding Engine...")

    test_messages = [
        "I want to sell 100 kg green apples from Srikakulam",
        "I want to sell 50 kg tomatoes",
        "I want to buy 100 kg red chillies",
        "status REQ004",
    ]

    for message in test_messages:
        print("\nUSER:", message)
        print(understand_farmer_message(message))
