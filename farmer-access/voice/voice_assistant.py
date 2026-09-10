import os
import sys


# ============================================================
# PATH SETUP
# ============================================================

CURRENT_DIRECTORY = os.path.dirname(
    os.path.abspath(__file__)
)

FARMER_ACCESS_DIRECTORY = os.path.abspath(
    os.path.join(
        CURRENT_DIRECTORY,
        ".."
    )
)

CORE_DIRECTORY = os.path.join(
    FARMER_ACCESS_DIRECTORY,
    "core"
)

VOICE_DIRECTORY = os.path.join(
    FARMER_ACCESS_DIRECTORY,
    "voice"
)

if CORE_DIRECTORY not in sys.path:
    sys.path.insert(
        0,
        CORE_DIRECTORY
    )

if VOICE_DIRECTORY not in sys.path:
    sys.path.insert(
        0,
        VOICE_DIRECTORY
    )


# ============================================================
# IMPORT CENTRAL ENGINE
# ============================================================

from access_engine import process_message
from speech_service import listen_to_farmer


# ============================================================
# TEXT TO SPEECH
# ============================================================

def speak_response(message):

    if not message:
        return

    try:

        import pyttsx3

        engine = pyttsx3.init()

        engine.setProperty(
            "rate",
            165
        )

        engine.say(
            str(message)
        )

        engine.runAndWait()

        engine.stop()

    except Exception as error:

        print(
            f"Voice output unavailable: {error}"
        )


# ============================================================
# DISPLAY RESULT
# ============================================================

def display_result(result):

    print()
    print("=" * 60)
    print("GRAINFLOW RESPONSE")
    print("=" * 60)

    message = result.get(
        "message"
    )

    if message:

        print()
        print(
            "GrainFlow:",
            message
        )

    request = result.get(
        "request"
    )

    if request:

        print()
        print(
            "-" * 60
        )

        print(
            "REQUEST DETAILS"
        )

        print(
            "-" * 60
        )

        print(
            f"Request ID : "
            f"{request.get('request_id')}"
        )

        print(
            f"Type       : "
            f"{request.get('request_type')}"
        )

        if request.get(
            "farmer_name"
        ):

            print(
                f"Farmer     : "
                f"{request.get('farmer_name')}"
            )

        if request.get(
            "buyer_name"
        ):

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
            "-" * 60
        )

    requests = result.get(
        "requests"
    )

    if requests:

        print()
        print(
            "TOTAL REQUESTS:",
            len(requests)
        )


# ============================================================
# VOICE ASSISTANT
# ============================================================

def run_voice_assistant():

    print()
    print("=" * 60)
    print("WELCOME TO GRAINFLOW VOICE ASSISTANT")
    print("=" * 60)

    welcome_message = (
        "Welcome to GrainFlow. "
        "You can tell me what you want to buy, "
        "sell, or track."
    )

    print()
    print(
        "GRAINFLOW:",
        welcome_message
    )

    speak_response(
        welcome_message
    )

    session_id = "voice"

    while True:

        try:

            print()
            print(
                "Press Enter to START recording "
                "or type exit to stop."
            )

            user_choice = input()

            if user_choice.strip().lower() == "exit":

                goodbye_message = (
                    "Thank you for using GrainFlow. "
                    "Goodbye."
                )

                print()
                print(
                    "GRAINFLOW:",
                    goodbye_message
                )

                speak_response(
                    goodbye_message
                )

                break

            voice_result = listen_to_farmer()

            if not isinstance(
                voice_result,
                dict
            ):

                print(
                    "Unable to process voice input."
                )

                continue

            if not voice_result.get(
                "success"
            ):

                error_message = (
                    "Sorry, I could not understand "
                    "your voice. Please try again."
                )

                print()
                print(
                    "GRAINFLOW:",
                    error_message
                )

                speak_response(
                    error_message
                )

                continue

            message = voice_result.get(
                "message"
            )

            if not message:

                continue

            print()
            print(
                "You said:",
                message
            )

            print()
            print(
                "Processing your request..."
            )

            result = process_message(
                message,
                session_id
            )

            display_result(
                result
            )

            response_message = result.get(
                "message"
            )

            if response_message:

                speak_response(
                    response_message
                )

            if message.strip().lower() in [
                "exit",
                "quit",
                "bye",
                "goodbye",
            ]:

                break

        except KeyboardInterrupt:

            print()
            print(
                "Voice assistant stopped."
            )

            break

        except Exception as error:

            print()
            print(
                "Voice assistant error:",
                error
            )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    run_voice_assistant()