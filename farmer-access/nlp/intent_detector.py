def detect_intent(message):

    # Handle empty messages
    if not message:
        return "UNKNOWN"

    message = message.lower()

    # Words and phrases related to selling grain
    sell_keywords = [
        "sell",
        "selling",
        "want to sell",
        "have grain to sell",
        "have rice to sell",
        "need to sell"
    ]

    # Words and phrases related to buying grain
    buy_keywords = [
        "buy",
        "buying",
        "purchase",
        "want to buy",
        "need to buy",
        "need to purchase"
    ]

    # Words and phrases related to checking request status
    status_keywords = [
        "status",
        "track",
        "tracking",
        "where is my request",
        "where is my order",
        "request progress",
        "order progress",
        "check my request"
    ]

    # Detect SELL_GRAIN intent
    if any(keyword in message for keyword in sell_keywords):
        return "SELL_GRAIN"

    # Detect BUY_GRAIN intent
    elif any(keyword in message for keyword in buy_keywords):
        return "BUY_GRAIN"

    # Detect CHECK_STATUS intent
    elif any(keyword in message for keyword in status_keywords):
        return "CHECK_STATUS"

    # Unknown request
    return "UNKNOWN"


if __name__ == "__main__":

    test_messages = [
        "I want to sell my rice",
        "I have 500 kg of rice to sell",
        "I need to purchase wheat",
        "Where is my request?",
        "Can I know my order progress?",
        "Hello, I need some help"
    ]

    for message in test_messages:

        result = detect_intent(message)

        print("Message:", message)
        print("Detected Intent:", result)
        print("-" * 40)