import os
import sys


# ============================================================
# PATH SETUP
# ============================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FARMER_ACCESS_DIR = os.path.dirname(CURRENT_DIR)

AI_DIR = os.path.join(FARMER_ACCESS_DIR, "ai")
ACTIONS_DIR = os.path.join(FARMER_ACCESS_DIR, "actions")
CORE_DIR = os.path.join(FARMER_ACCESS_DIR, "core")

for path in [AI_DIR, ACTIONS_DIR, CORE_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)


# ============================================================
# IMPORT SERVICES
# ============================================================

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from gemini_service import understand_farmer_message
from smart_parser import smart_parse_message
from action_router import route_action
from validation import (
    validate_sell_details,
    validate_buy_details,
    validate_check_status_details,
    validate_update_status_details,
    validate_quantity,
)


# ============================================================
# CONVERSATION SESSIONS
# ============================================================

CONVERSATION_SESSIONS = {}


# ============================================================
# REQUIRED FIELDS
# ============================================================

REQUIRED_FIELDS = {

    "SELL_GRAIN": [
        "farmer_name",
        "grain_type",
        "quantity",
        "location"
    ],

    "BUY_GRAIN": [
        "buyer_name",
        "grain_type",
        "quantity",
        "location"
    ],

    "CHECK_STATUS": [
        "request_id"
    ],

    "UPDATE_STATUS": [
        "request_id",
        "status"
    ],

    "GET_ALL_REQUESTS": []
}


SESSION_OVERRIDE_INTENTS = {
    "SELL_GRAIN",
    "BUY_GRAIN",
    "CHECK_STATUS",
    "UPDATE_STATUS",
    "GET_ALL_REQUESTS",
}


# ============================================================
# CREATE EMPTY DETAILS
# ============================================================

def create_empty_details(intent):

    if intent == "SELL_GRAIN":

        return {
            "farmer_name": None,
            "grain_type": None,
            "quantity": None,
            "location": None
        }

    elif intent == "BUY_GRAIN":

        return {
            "buyer_name": None,
            "grain_type": None,
            "quantity": None,
            "location": None
        }

    elif intent == "CHECK_STATUS":

        return {
            "request_id": None
        }

    elif intent == "UPDATE_STATUS":

        return {
            "request_id": None,
            "status": None
        }

    elif intent == "GET_ALL_REQUESTS":
        return {}

    return {}


# ============================================================
# GET SESSION
# ============================================================

def get_session(session_id):

    if session_id not in CONVERSATION_SESSIONS:

        CONVERSATION_SESSIONS[session_id] = {
            "intent": None,
            "details": {}
        }

    return CONVERSATION_SESSIONS[session_id]


# ============================================================
# CLEAR SESSION
# ============================================================

def clear_session(session_id):

    if session_id in CONVERSATION_SESSIONS:
        del CONVERSATION_SESSIONS[session_id]


# ============================================================
# MERGE DETAILS
# ============================================================

def merge_details(old_details, new_details):

    if old_details is None:
        old_details = {}

    if new_details is None:
        return old_details

    for key, value in new_details.items():

        if value is None:
            continue

        if isinstance(value, str):

            value = value.strip()

            if value == "":
                continue

        old_details[key] = value

    return old_details


# ============================================================
# NORMALIZE INTENT
# ============================================================

def normalize_intent(intent):

    if intent is None:
        return None

    intent = str(intent).strip().upper()

    replacements = {

        "SELL": "SELL_GRAIN",
        "SELL PRODUCT": "SELL_GRAIN",
        "SELL FOOD": "SELL_GRAIN",
        "SELL GRAIN": "SELL_GRAIN",

        "BUY": "BUY_GRAIN",
        "BUY PRODUCT": "BUY_GRAIN",
        "BUY FOOD": "BUY_GRAIN",
        "BUY GRAIN": "BUY_GRAIN",

        "STATUS": "CHECK_STATUS",
        "CHECK STATUS": "CHECK_STATUS",
        "CHECK_REQUEST_STATUS": "CHECK_STATUS",
        "TRACK": "CHECK_STATUS",

        "UPDATE STATUS": "UPDATE_STATUS",
        "GET ALL REQUESTS": "GET_ALL_REQUESTS",
        "LIST REQUESTS": "GET_ALL_REQUESTS",
        "SHOW ALL REQUESTS": "GET_ALL_REQUESTS",
    }

    return replacements.get(intent, intent)


# ============================================================
# NORMALIZE AI RESULT
# ============================================================

def normalize_ai_result(result):

    if result is None:
        return None

    if not isinstance(result, dict):
        return None

    if isinstance(result.get("data"), dict):
        result = result["data"]

    # --------------------------------------------------------
    # FIND INTENT
    # --------------------------------------------------------

    intent = (
        result.get("intent")
        or result.get("action")
        or result.get("request_type")
    )

    intent = normalize_intent(intent)

    if intent in {"RESET", "EXIT"}:
        return {
            "intent": intent,
            "details": {}
        }

    # --------------------------------------------------------
    # FIND DETAILS
    # --------------------------------------------------------

    details = result.get("details")

    if not isinstance(details, dict):
        details = {}

    # --------------------------------------------------------
    # DIRECT FIELDS FROM AI
    # --------------------------------------------------------

    possible_fields = [

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
    ]

    for field in possible_fields:

        if field in result and field not in details:

            details[field] = result[field]

    # --------------------------------------------------------
    # NORMALIZE PERSON NAME
    # --------------------------------------------------------

    if details.get("person_name"):

        person_name = details.get("person_name")

        if intent == "BUY_GRAIN":

            details["buyer_name"] = person_name

        else:

            details["farmer_name"] = person_name

    # --------------------------------------------------------
    # NORMALIZE PRODUCT
    # --------------------------------------------------------

    if details.get("commodity"):

        if not details.get("grain_type"):

            details["grain_type"] = details["commodity"]

    if details.get("product"):

        if not details.get("grain_type"):

            details["grain_type"] = details["product"]

    # --------------------------------------------------------
    # REMOVE TEMPORARY FIELDS
    # --------------------------------------------------------

    details.pop("person_name", None)
    details.pop("commodity", None)
    details.pop("product", None)

    return {
        "intent": intent,
        "details": details
    }


# ============================================================
# FIND MISSING INFORMATION
# ============================================================

def find_missing_information(intent, details):

    required_fields = REQUIRED_FIELDS.get(
        intent,
        []
    )

    missing = []

    for field in required_fields:

        value = details.get(field)

        if value is None:

            missing.append(field)

        elif isinstance(value, str):

            if value.strip() == "":

                missing.append(field)

        elif field == "quantity":

            quantity_ok, _ = validate_quantity(value)

            if not quantity_ok:
                missing.append(field)

    return missing


# ============================================================
# CREATE QUESTION FOR MISSING INFORMATION
# ============================================================

def create_missing_information_message(
    intent,
    missing
):

    if not missing:
        return None

    field = missing[0]

    questions = {

        "farmer_name":
            "What is your name?",

        "buyer_name":
            "What is your name?",

        "grain_type":
            "What food or agricultural product do you want to sell or buy?",

        "quantity":
            "How much quantity do you want to sell or buy?",

        "location":
            "What is your location?",

        "request_id":
            "Please provide your request ID, for example REQ001.",

        "status":
            "What status should the request be updated to?",
    }

    return questions.get(
        field,
        f"Please provide your {field.replace('_', ' ')}."
    )


# ============================================================
# HANDLE CONTEXTUAL ANSWER
# ============================================================

def handle_contextual_answer(
    message,
    intent,
    details
):

    """
    Handles short answers based on the previous
    conversation context.

    Example:

    System:
        What is your name?

    User:
        Ramesh

    The system understands that Ramesh = farmer_name.
    """

    missing = find_missing_information(
        intent,
        details
    )

    if not missing:
        return details

    field = missing[0]

    text = message.strip()

    if not text:
        return details

    # --------------------------------------------------------
    # NAME
    # --------------------------------------------------------

    if field == "farmer_name":

        details["farmer_name"] = text

        return details

    if field == "buyer_name":

        details["buyer_name"] = text

        return details

    # --------------------------------------------------------
    # LOCATION
    # --------------------------------------------------------

    if field == "location":

        details["location"] = text

        return details

    # --------------------------------------------------------
    # PRODUCT
    # --------------------------------------------------------

    if field == "grain_type":

        details["grain_type"] = text

        return details

    # --------------------------------------------------------
    # REQUEST ID
    # --------------------------------------------------------

    if field == "request_id":

        details["request_id"] = text.upper()

        return details

    # --------------------------------------------------------
    # QUANTITY
    # --------------------------------------------------------

    if field == "quantity":

        import re

        match = re.search(
            r"\d+(?:\.\d+)?",
            text
        )

        if match:

            details["quantity"] = float(
                match.group()
            )

        return details

    if field == "status":

        details["status"] = text.upper().replace("-", "_").replace(" ", "_")

        return details

    return details


# ============================================================
# SPECIAL COMMANDS
# ============================================================

def handle_special_command(
    message,
    session_id
):

    text = message.strip().lower()

    # --------------------------------------------------------
    # EXIT
    # --------------------------------------------------------

    if text in [
        "exit",
        "quit",
        "bye",
        "goodbye"
    ]:

        clear_session(session_id)

        return {
            "handled": True,
            "success": True,
            "message":
                "Thank you for using GrainFlow. Goodbye."
        }

    # --------------------------------------------------------
    # RESET
    # --------------------------------------------------------

    if text in [
        "reset",
        "restart",
        "start over"
    ]:

        clear_session(session_id)

        return {
            "handled": True,
            "success": True,
            "message":
                "Okay. Let's start a new GrainFlow request."
        }

    # --------------------------------------------------------
    # CANCEL
    # --------------------------------------------------------

    if text in [
        "cancel",
        "cancel request",
        "stop"
    ]:

        clear_session(session_id)

        return {
            "handled": True,
            "success": True,
            "message":
                "Your current request has been cancelled."
        }

    return {
        "handled": False
    }


# ============================================================
# UNDERSTAND MESSAGE
# ============================================================

def understand_message(message):

    try:

        result = understand_farmer_message(
            message
        )

        normalized = normalize_ai_result(
            result
        )

        if normalized and normalized.get("intent"):

            return normalized

    except Exception as error:

        print(
            f"Understanding error: {error}"
        )

    try:

        result = smart_parse_message(
            message
        )

        normalized = normalize_ai_result(
            result
        )

        if normalized and normalized.get("intent"):

            return normalized

    except Exception as error:

        print(
            f"Smart Parser error: {error}"
        )

    return {
        "intent": None,
        "details": {}
    }


def validate_details_for_intent(intent, details):

    if intent == "SELL_GRAIN":
        return validate_sell_details(details)

    if intent == "BUY_GRAIN":
        return validate_buy_details(details)

    if intent == "CHECK_STATUS":
        return validate_check_status_details(details)

    if intent == "UPDATE_STATUS":
        return validate_update_status_details(details)

    if intent == "GET_ALL_REQUESTS":
        return True, None, {}

    return False, f"Unsupported action '{intent}'.", details or {}


# ============================================================
# EXECUTE ACTION
# ============================================================

def execute_action(
    intent,
    details,
    session_id
):

    valid, error_message, cleaned_details = (
        validate_details_for_intent(
            intent,
            details or {}
        )
    )

    if not valid:

        return {
            "success": False,
            "completed": False,
            "action": intent,
            "message": error_message,
        }

    if cleaned_details:
        details = cleaned_details

    try:

        action_result = route_action(
            intent,
            details
        )

    except Exception as error:

        print(f"Action execution error: {error}")

        return {
            "success": False,
            "completed": False,
            "message":
                "Unable to process your request. Please try again.",
        }

    response = action_result.get(
        "response",
        {}
    )

    if not isinstance(response, dict):
        response = {
            "success": False,
            "message": str(response),
        }

    success = response.get(
        "success",
        False
    )

    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    if success:

        clear_session(session_id)

        result = {
            "success": True,
            "completed": True,
            "action":
                action_result.get("action"),
            "message":
                response.get(
                    "message",
                    "Request completed successfully."
                ),
        }

        if response.get("request") is not None:
            result["request"] = response.get("request")

        if response.get("requests") is not None:
            result["requests"] = response.get("requests")

        return result

    # --------------------------------------------------------
    # FAILURE
    # --------------------------------------------------------

    return {
        "success": False,
        "completed": False,
        "action":
            action_result.get("action"),
        "message":
            response.get(
                "message",
                "Unable to process your request."
            )
    }


# ============================================================
# PROCESS MESSAGE
# ============================================================

def process_message(
    message,
    session_id="default"
):

    # --------------------------------------------------------
    # VALIDATE MESSAGE
    # --------------------------------------------------------

    if message is None:

        return {
            "success": False,
            "message":
                "Please enter a message."
        }

    message = str(message).strip()

    if not message:

        return {
            "success": False,
            "message":
                "Please enter a message."
        }

    # --------------------------------------------------------
    # SPECIAL COMMANDS
    # --------------------------------------------------------

    special = handle_special_command(
        message,
        session_id
    )

    if special["handled"]:

        return special

    # --------------------------------------------------------
    # GET CURRENT SESSION
    # --------------------------------------------------------

    session = get_session(
        session_id
    )

    current_intent = session.get(
        "intent"
    )

    current_details = session.get(
        "details",
        {}
    )

    # ========================================================
    # IMPORTANT:
    # HANDLE SHORT ANSWER USING EXISTING CONTEXT
    # ========================================================

    parsed_message = None

    if current_intent:

        missing_before_parser = (
            find_missing_information(
                current_intent,
                current_details
            )
        )

        if missing_before_parser:

            parsed_message = understand_message(message)

            parsed_intent = parsed_message.get("intent")

            should_override_session = (
                parsed_intent in SESSION_OVERRIDE_INTENTS
                and parsed_intent != current_intent
            )

            if not should_override_session:

                current_details = (
                    handle_contextual_answer(
                        message,
                        current_intent,
                        current_details
                    )
                )

                session["details"] = (
                    current_details
                )

                missing_after_answer = (
                    find_missing_information(
                        current_intent,
                        current_details
                    )
                )

                if not missing_after_answer:

                    return execute_action(
                        current_intent,
                        current_details,
                        session_id
                    )

                return {
                    "success": True,
                    "completed": False,
                    "intent":
                        current_intent,
                    "details":
                        current_details,
                    "missing":
                        missing_after_answer,
                    "message":
                        create_missing_information_message(
                            current_intent,
                            missing_after_answer
                        )
                }

            clear_session(session_id)

            session = get_session(session_id)

            current_intent = session.get("intent")

            current_details = session.get("details", {})

    # ========================================================
    # UNDERSTAND NEW MESSAGE
    # ========================================================

    ai_result = parsed_message or understand_message(
        message
    )

    new_intent = ai_result.get(
        "intent"
    )

    new_details = ai_result.get(
        "details",
        {}
    )

    # ========================================================
    # NEW INTENT FOUND
    # ========================================================

    if new_intent:

        if new_intent not in REQUIRED_FIELDS:

            return {
                "success": False,
                "message":
                    "I understood your message, "
                    "but I couldn't determine the required action."
            }

        # ----------------------------------------------------
        # NEW REQUEST
        # ----------------------------------------------------

        if session.get("intent") != new_intent:

            current_details = (
                create_empty_details(
                    new_intent
                )
            )

        current_intent = new_intent

        current_details = merge_details(
            current_details,
            new_details
        )

        session["intent"] = (
            current_intent
        )

        session["details"] = (
            current_details
        )

    else:

        # ====================================================
        # NO NEW INTENT
        # ====================================================

        if current_intent:

            current_details = merge_details(
                current_details,
                new_details
            )

            session["details"] = (
                current_details
            )

        else:

            return {
                "success": False,
                "message":
                    "I couldn't understand your request. "
                    "Please tell me whether you want to "
                    "sell, buy, or check a request status."
            }

    # ========================================================
    # FIND REMAINING INFORMATION
    # ========================================================

    missing = find_missing_information(
        current_intent,
        current_details
    )

    # ========================================================
    # ASK NEXT QUESTION
    # ========================================================

    if missing:

        return {
            "success": True,
            "completed": False,
            "intent":
                current_intent,
            "details":
                current_details,
            "missing":
                missing,
            "message":
                create_missing_information_message(
                    current_intent,
                    missing
                )
        }

    # ========================================================
    # EVERYTHING IS AVAILABLE
    # ========================================================

    return execute_action(
        current_intent,
        current_details,
        session_id
    )


# ============================================================
# DISPLAY RESULT
# ============================================================

def display_result(result):

    print("\nGRAINFLOW:")

    message = result.get(
        "message"
    )

    if message:

        print(message)

    request = result.get(
        "request"
    )

    if request:

        print(
            "\n----------------------------------------"
        )

        print(
            "REQUEST DETAILS"
        )

        print(
            "----------------------------------------"
        )

        print(
            f"Request ID : "
            f"{request.get('request_id')}"
        )

        print(
            f"Type       : "
            f"{request.get('request_type')}"
        )

        if request.get("farmer_name"):

            print(
                f"Farmer     : "
                f"{request.get('farmer_name')}"
            )

        if request.get("buyer_name"):

            print(
                f"Buyer      : "
                f"{request.get('buyer_name')}"
            )

        print(
            f"Product    : "
            f"{request.get('grain_type')}"
        )

        print(
            f"Quantity   : "
            f"{request.get('quantity')}"
        )

        print(
            f"Location   : "
            f"{request.get('location')}"
        )

        print(
            f"Status     : "
            f"{request.get('status')}"
        )

        print(
            f"Created    : "
            f"{request.get('created_at')}"
        )

        print(
            "----------------------------------------"
        )


# ============================================================
# INTERACTIVE TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\n=========================================="
    )

    print(
        "       GrainFlow Central Access Engine"
    )

    print(
        "=========================================="
    )

    print("\nYou can:")

    print(
        "• Sell agricultural products"
    )

    print(
        "• Buy agricultural products"
    )

    print(
        "• Check request status"
    )

    print(
        "• Update request status"
    )

    print(
        "• List all requests"
    )

    print(
        "• Continue a request over multiple messages"
    )

    print(
        "• Type 'reset' to restart"
    )

    print(
        "• Type 'exit' to quit"
    )

    session_id = "terminal_user"

    while True:

        try:

            message = input(
                "\nYOU: "
            )

        except KeyboardInterrupt:

            print(
                "\n\nThank you for using GrainFlow. Goodbye."
            )

            break

        except EOFError:

            break

        result = process_message(
            message,
            session_id
        )

        display_result(
            result
        )

        if message.strip().lower() in [
            "exit",
            "quit",
            "bye",
            "goodbye"
        ]:

            break