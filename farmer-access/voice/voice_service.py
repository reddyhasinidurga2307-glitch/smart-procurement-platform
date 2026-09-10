import sys
import os


base_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

nlp_path = os.path.join(
    base_path,
    "nlp"
)

actions_path = os.path.join(
    base_path,
    "actions"
)

conversation_path = os.path.join(
    base_path,
    "conversation"
)


sys.path.append(nlp_path)
sys.path.append(actions_path)
sys.path.append(conversation_path)


from intent_detector import detect_intent
from entity_extractor import extract_entities
from missing_info_detector import find_missing_information
from action_router import route_action

from conversation_manager import (
    start_conversation,
    update_conversation,
    get_conversation,
    clear_conversation
)


def process_farmer_voice(message, additional_details=None):

    if not message:
        return {
            "success": False,
            "message": "No voice message received"
        }

    message_details = extract_entities(message)

    detected_intent = detect_intent(message)

    conversation = get_conversation()

    # Check whether the user started a new request
    if conversation:

        current_intent = conversation.get("intent")

        if (
            detected_intent != "UNKNOWN"
            and detected_intent != current_intent
        ):

            clear_conversation()
            conversation = {}

    # Start a new conversation
    if not conversation:

        if detected_intent == "UNKNOWN":

            return {
                "success": False,
                "original_message": message,
                "detected_intent": "UNKNOWN",
                "message": "Sorry, I could not understand your request"
            }

        intent = detected_intent

        start_conversation(
            intent,
            message_details
        )

    else:

        intent = conversation.get("intent")

    # Add extra details such as farmer name or buyer name
    if additional_details:

        message_details.update(
            additional_details
        )

    # Update the conversation without deleting old information
    update_conversation(
        message_details
    )

    # Get the latest conversation data
    conversation = get_conversation()

    intent = conversation.get("intent")

    details = conversation.get("details")

    # Find missing information
    missing_information = find_missing_information(
        intent,
        details
    )

    # Ask for missing information
    if missing_information:

        return {
            "success": False,
            "original_message": message,
            "detected_intent": intent,
            "details": details,
            "missing_information": missing_information,
            "message": (
                "Please provide: "
                + ", ".join(missing_information)
            )
        }

    # All information is available
    action_result = route_action(
        intent,
        details
    )

    # Clear conversation after successful completion
    clear_conversation()

    return {
        "success": True,
        "original_message": message,
        "detected_intent": intent,
        "details": details,
        "action": action_result.get("action"),
        "response": action_result.get("response")
    }


if __name__ == "__main__":

    print("TEST 1: SELL_GRAIN MULTI-TURN")
    print()

    sell_messages = [
        (
            "I want to sell rice",
            None
        ),
        (
            "500 kg from Bhimavaram",
            None
        ),
        (
            "Ramesh",
            {
                "farmer_name": "Ramesh"
            }
        )
    ]

    for message, additional_details in sell_messages:

        print("Farmer:", message)

        result = process_farmer_voice(
            message,
            additional_details
        )

        print("System:")
        print(result)

        print("-" * 60)


    print()
    print("TEST 2: BUY_GRAIN MULTI-TURN")
    print()

    buy_messages = [
        (
            "I want to buy wheat",
            None
        ),
        (
            "300 kg in Hyderabad",
            None
        ),
        (
            "Suresh",
            {
                "buyer_name": "Suresh"
            }
        )
    ]

    for message, additional_details in buy_messages:

        print("Buyer:", message)

        result = process_farmer_voice(
            message,
            additional_details
        )

        print("System:")
        print(result)

        print("-" * 60)