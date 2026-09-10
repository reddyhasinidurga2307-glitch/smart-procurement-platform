import re


def extract_entities(message):

    if not message:
        return {
            "grain_type": None,
            "quantity": None,
            "location": None,
            "request_id": None
        }

    message_lower = message.lower().strip()

    grain_type = None
    quantity = None
    location = None
    request_id = None

    # ---------------------------------
    # Extract quantity
    # ---------------------------------

    quantity_match = re.search(
        r"\b(\d+(?:\.\d+)?)\s*(kg|kgs|kilogram|kilograms|ton|tons|tonne|tonnes)\b",
        message_lower
    )

    if quantity_match:
        quantity_value = quantity_match.group(1)

        if "." in quantity_value:
            quantity = float(quantity_value)
        else:
            quantity = int(quantity_value)

    # ---------------------------------
    # Extract request ID
    # ---------------------------------

    request_match = re.search(
        r"\bREQ\d+\b",
        message.upper()
    )

    if request_match:
        request_id = request_match.group()

    # ---------------------------------
    # Extract location
    # ---------------------------------

    locations = [
        "bhimavaram",
        "hyderabad",
        "vijayawada",
        "visakhapatnam",
        "rajahmundry",
        "srikakulam",
        "tirupati",
        "guntur",
        "eluru",
        "kakinada"
    ]

    for city in locations:
        if city in message_lower:
            location = city.title()
            break

    # ---------------------------------
    # Extract commodity
    # ---------------------------------

    # Remove known information so that
    # the remaining meaningful words can
    # be used to identify the commodity.

    cleaned_message = message_lower

    cleaned_message = re.sub(
        r"\b(\d+(?:\.\d+)?)\s*(kg|kgs|kilogram|kilograms|ton|tons|tonne|tonnes)\b",
        " ",
        cleaned_message
    )

    for city in locations:
        cleaned_message = cleaned_message.replace(
            city,
            " "
        )

    cleaned_message = re.sub(
        r"\b(sell|selling|buy|buying|purchase|purchasing|want|need|have|to|my|some|of|the|a|an|i|from|in|at|location)\b",
        " ",
        cleaned_message
    )

    cleaned_message = re.sub(
        r"\s+",
        " ",
        cleaned_message
    ).strip()

    # Ignore status-related requests
    status_words = [
        "status",
        "track",
        "tracking",
        "request",
        "order",
        "progress",
        "where"
    ]

    words = cleaned_message.split()

    commodity_words = [
        word
        for word in words
        if word not in status_words
        and not word.upper().startswith("REQ")
    ]

    if commodity_words:
        grain_type = " ".join(
            commodity_words
        ).title()

    return {
        "grain_type": grain_type,
        "quantity": quantity,
        "location": location,
        "request_id": request_id
    }


if __name__ == "__main__":

    test_messages = [
        "I want to sell 60 kg tomatoes from Bhimavaram",
        "I want to sell 100 kg dragon fruit from Vijayawada",
        "I have 50 kg chillies",
        "I want to buy 200 kg wheat in Hyderabad",
        "I have 500 kg mangoes from Srikakulam",
        "What is the status of request REQ002?"
    ]

    for message in test_messages:
        result = extract_entities(message)

        print("Message:", message)
        print("Extracted Entities:", result)
        print("-" * 60)