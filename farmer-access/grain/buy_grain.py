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

sys.path.append(nlp_path)

from missing_info_detector import find_missing_information


def create_buy_request(
    buyer_name,
    grain_type,
    quantity,
    location
):

    buyer_details = {
        "buyer_name": buyer_name,
        "grain_type": grain_type,
        "quantity": quantity,
        "location": location
    }

    missing_information = find_missing_information(
        "BUY_GRAIN",
        buyer_details
    )

    if missing_information:

        return {
            "success": False,
            "message": "Please provide: " +
            ", ".join(missing_information)
        }

    request = {
        "buyer_name": buyer_name,
        "grain_type": grain_type,
        "quantity": quantity,
        "location": location,
        "status": "REQUEST_CREATED"
    }

    return {
        "success": True,
        "message": "Grain buying request created successfully",
        "request": request
    }


if __name__ == "__main__":

    result = create_buy_request(
        buyer_name="Suresh",
        grain_type="Wheat",
        quantity=300,
        location="Hyderabad"
    )

    print(result)