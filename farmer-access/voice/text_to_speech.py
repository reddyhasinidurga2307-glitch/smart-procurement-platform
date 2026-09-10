import os
import sys


BASE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

VOICE_PATH = os.path.join(BASE_PATH, "voice")
CONVERSATION_PATH = os.path.join(BASE_PATH, "conversation")

for path in [VOICE_PATH, CONVERSATION_PATH]:
    if path not in sys.path:
        sys.path.append(path)


from speech_service import listen_to_farmer
from text_to_speech import speak_message
from voice_service import process_farmer_voice
from conversation_manager import (
    start_conversation,
    update_conversation,
    get_conversation,
    clear_conversation
)


def say_and_print(message):
    print()
    print("GRAINFLOW:", message)
    speak_message(message)


def run_voice_assistant():
    print("=" * 60)
    print("WELCOME TO GRAINFLOW VOICE ASSISTANT")
    print("=" * 60)

    say_and_print(
        "Welcome to GrainFlow. Please speak your grain request."
    )

    clear_conversation()

    while True:
        print()

        voice_result = listen_to_farmer()

        if not voice_result.get("success"):
            error_message = voice_result.get(
                "message",
                "Sorry, I could not understand your voice."
            )

            say_and_print(error_message)
            continue

        farmer_message = voice_result.get("message")

        if not farmer_message:
            say_and_print(
                "Sorry, I could not understand your voice."
            )
            continue

        print()
        print("Processing your request...")

        conversation = get_conversation()

        if not conversation:
            system_result = process_farmer_voice(
                farmer_message
            )
        else:
            existing_details = conversation.get(
                "details",
                {}
            )

            system_result = process_farmer_voice(
                farmer_message,
                existing_details
            )

        print()
        print("GRAINFLOW RESPONSE:")
        print(system_result)

        if system_result.get("success"):
            response = system_result.get("response")

            if isinstance(response, dict):
                response_message = response.get(
                    "message",
                    "Your request was completed successfully."
                )
            else:
                response_message = (
                    "Your request was completed successfully."
                )

            say_and_print(response_message)

            clear_conversation()

            print()
            say_and_print(
                "You can speak another request now."
            )

            continue

        detected_intent = system_result.get(
            "detected_intent"
        )

        if detected_intent == "UNKNOWN":
            message = system_result.get(
                "message",
                "Sorry, I could not understand your request. Please try again."
            )

            say_and_print(message)
            continue

        details = system_result.get(
            "details",
            {}
        )

        if not conversation:
            start_conversation(
                detected_intent,
                details
            )
        else:
            update_conversation(details)

        missing_information = system_result.get(
            "missing_information",
            []
        )

        if missing_information:
            readable_fields = []

            for field in missing_information:
                field_name = field.replace(
                    "_",
                    " "
                )

                readable_fields.append(field_name)

            message = (
                "Please provide your "
                + ", ".join(readable_fields)
            )

            say_and_print(message)
        else:
            say_and_print(
                "Please provide more information."
            )


if __name__ == "__main__":
    try:
        run_voice_assistant()

    except KeyboardInterrupt:
        print()
        print("GRAINFLOW: Voice assistant stopped.")

        try:
            speak_message(
                "GrainFlow voice assistant stopped."
            )
        except Exception:
            pass