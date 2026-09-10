def find_missing_information(intent, details):

    if not details:
        details = {}

    required_fields = []

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

    missing_information = []

    for field in required_fields:
        if not details.get(field):
            missing_information.append(field)

    return missing_information


if __name__ == "__main__":

    sell_details = {
        "farmer_name": "Ramesh",
        "grain_type": "Rice",
        "quantity": None,
        "location": None
    }

    buy_details = {
        "buyer_name": None,
        "grain_type": "Wheat",
        "quantity": 300,
        "location": "Hyderabad"
    }

    status_details = {
        "request_id": None
    }

    print("SELL_GRAIN Missing Information:")
    print(
        find_missing_information(
            "SELL_GRAIN",
            sell_details
        )
    )

    print()

    print("BUY_GRAIN Missing Information:")
    print(
        find_missing_information(
            "BUY_GRAIN",
            buy_details
        )
    )

    print()

    print("CHECK_STATUS Missing Information:")
    print(
        find_missing_information(
            "CHECK_STATUS",
            status_details
        )
    )