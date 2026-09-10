import os
import re
import sys


CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

PROJECT_DIRECTORY = os.path.abspath(
    os.path.join(CURRENT_DIRECTORY, "..")
)

sys.path.append(
    os.path.join(PROJECT_DIRECTORY, "actions")
)

from action_router import route_action


# Each phone number gets its own conversation
SMS_SESSIONS = {}


def get_session(phone_number):

    if phone_number not in SMS_SESSIONS:

        SMS_SESSIONS[phone_number] = {
            "intent": None,
            "details": {
                "grain_type": None,
                "quantity": None,
                "location": None,
                "farmer_name": None,
                "buyer_name": None,
                "request_id": None
            }
        }

    return SMS_SESSIONS[phone_number]


def extract_intent(message):

    message = message.lower()

    if any(
        word in message
        for word in ["sell", "selling", "have to sell"]
    ):

        return "SELL_GRAIN"

    if any(
        word in message
        for word in ["buy", "purchase", "need to buy"]
    ):

        return "BUY_GRAIN"

    if any(
        word in message
        for word in ["status", "track", "check request"]
    ):

        return "CHECK_STATUS"

    return None


def extract_quantity(message):

    match = re.search(
        r"\b(\d+(?:\.\d+)?)\s*(kg|kgs|kilogram|kilograms|ton|tons)?\b",
        message,
        re.IGNORECASE
    )

    if match:

        value = float(match.group(1))

        if value.is_integer():

            return int(value)

        return value

    return None


def extract_location(message):

    patterns = [
        r"\bfrom\s+([A-Za-z\s]+)",
        r"\bin\s+([A-Za-z\s]+)",
        r"\blocation\s+([A-Za-z\s]+)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            message,
            re.IGNORECASE
        )

        if match:

            location = match.group(1).strip()

            # Remove common extra words
            location = re.split(
                r"\b(and|my|i|with|quantity)\b",
                location,
                flags=re.IGNORECASE
            )[0].strip()

            if location:

                return location.title()

    return None


def extract_name(message):

    patterns = [
        r"\bmy name is\s+([A-Za-z\s]+)",
        r"\bi am\s+([A-Za-z\s]+)",
        r"\bi'm\s+([A-Za-z\s]+)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            message,
            re.IGNORECASE
        )

        if match:

            name = match.group(1).strip()

            # Remove unrelated words
            name = re.split(
                r"\b(from|in|sell|buy|kg|kgs)\b",
                name,
                flags=re.IGNORECASE
            )[0].strip()

            if name:

                return name.title()

    return None


def extract_request_id(message):

    match = re.search(
        r"\bREQ[- ]?\d+\b",
        message,
        re.IGNORECASE
    )

    if match:

        return match.group(0).upper().replace(
            " ",
            ""
        )

    return None


def extract_commodity(message):

    message = message.lower()

    patterns = [
        r"sell\s+(?:\d+(?:\.\d+)?\s*(?:kg|kgs|kilograms?|tons?)\s+)?(?:of\s+)?([a-zA-Z\s]+?)(?:\s+from|\s+in|$)",
        r"buy\s+(?:\d+(?:\.\d+)?\s*(?:kg|kgs|kilograms?|tons?)\s+)?(?:of\s+)?([a-zA-Z\s]+?)(?:\s+from|\s+in|$)",
        r"have\s+([a-zA-Z\s]+?)\s+to\s+sell"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            message,
            re.IGNORECASE
        )

        if match:

            commodity = match.group(1).strip()

            # Remove unnecessary words
            remove_words = [
                "fresh",
                "organic"
            ]

            # Keep original commodity but clean spaces
            commodity = re.sub(
                r"\s+",
                " ",
                commodity
            ).strip()

            if commodity:

                return commodity.lower()

    return None


def update_session(session, message):

    detected_intent = extract_intent(message)

    if detected_intent:

        session["intent"] = detected_intent

    details = session["details"]

    quantity = extract_quantity(message)

    if quantity is not None:

        details["quantity"] = quantity

    location = extract_location(message)

    if location:

        details["location"] = location

    name = extract_name(message)

    if name:

        if session["intent"] == "BUY_GRAIN":

            details["buyer_name"] = name

        else:

            details["farmer_name"] = name

    request_id = extract_request_id(message)

    if request_id:

        details["request_id"] = request_id

    commodity = extract_commodity(message)

    if commodity:

        details["grain_type"] = commodity

    return session


def get_missing_information(session):

    intent = session["intent"]

    details = session["details"]

    if intent == "SELL_GRAIN":

        required_fields = [
            "farmer_name",
            "grain_type",
            "quantity",
            "location"
        ]

    elif intent == "BUY_GRAIN":

        required_fields = [
            "buyer_name",
            "grain_type",
            "quantity",
            "location"
        ]

    elif intent == "CHECK_STATUS":

        required_fields = [
            "request_id"
        ]

    else:

        return ["request_type"]

    missing = []

    for field in required_fields:

        if details.get(field) is None:

            missing.append(field)

    return missing


def create_missing_message(missing):

    names = {
        "farmer_name": "your name",
        "buyer_name": "your name",
        "grain_type": "the food item",
        "quantity": "the quantity",
        "location": "your location",
        "request_id": "your request ID",
        "request_type": "whether you want to sell, buy, or check status"
    }

    readable = [
        names.get(field, field)
        for field in missing
    ]

    if len(readable) == 1:

        return "Please provide " + readable[0] + "."

    if len(readable) == 2:

        return (
            "Please provide "
            + readable[0]
            + " and "
            + readable[1]
            + "."
        )

    return (
        "Please provide "
        + ", ".join(readable[:-1])
        + ", and "
        + readable[-1]
        + "."
    )


def process_sms(phone_number, message):

    if not phone_number:

        return {
            "success": False,
            "response": "Phone number is required."
        }

    if not message or not message.strip():

        return {
            "success": False,
            "response": "Please send a message."
        }

    session = get_session(phone_number)

    update_session(
        session,
        message.strip()
    )

    missing = get_missing_information(session)

    if missing:

        return {
            "success": False,
            "phone_number": phone_number,
            "received_message": message,
            "intent": session["intent"],
            "details": session["details"],
            "missing_information": missing,
            "response": create_missing_message(missing)
        }

    try:

        action_result = route_action(
            session["intent"],
            session["details"]
        )

        # Clear session after successful completion
        del SMS_SESSIONS[phone_number]

        response = "Your request has been processed successfully."

        if isinstance(action_result, dict):

            nested = action_result.get(
                "response"
            )

            if isinstance(nested, dict):

                response = nested.get(
                    "message",
                    response
                )

            elif action_result.get("message"):

                response = action_result.get(
                    "message"
                )

        return {
            "success": True,
            "phone_number": phone_number,
            "received_message": message,
            "intent": session["intent"],
            "details": session["details"],
            "response": response
        }

    except Exception as error:

        return {
            "success": False,
            "phone_number": phone_number,
            "response": "Unable to process the request.",
            "error": str(error)
        }


if __name__ == "__main__":

    print("=" * 60)
    print("GRAINFLOW SMS ACCESS")
    print("=" * 60)

    phone_number = "+919999999999"

    test_messages = [
        "I want to sell 100 kg of tomatoes from Bhimavaram",
        "My name is Ramesh"
    ]

    for message in test_messages:

        print()
        print("FARMER SMS:")
        print(message)

        result = process_sms(
            phone_number,
            message
        )

        print()
        print("GRAINFLOW SMS RESPONSE:")
        print(result)

        print("-" * 60)