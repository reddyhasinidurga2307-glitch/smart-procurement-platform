import os
import sys


# ============================================================
# PATH SETUP
# ============================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FARMER_ACCESS_DIR = os.path.dirname(CURRENT_DIR)
CORE_DIR = os.path.join(FARMER_ACCESS_DIR, "core")

if CORE_DIR not in sys.path:
    sys.path.insert(0, CORE_DIR)


# ============================================================
# REQUEST STORE
# ============================================================

from request_store import (
    create_request,
    get_request,
    get_all_requests,
    update_request_status,
)
from validation import (
    validate_sell_details,
    validate_buy_details,
    validate_check_status_details,
    validate_update_status_details,
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_value(value):
    """
    Convert a value into a clean string.
    """

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    return value


def clean_quantity(value):
    """
    Convert quantity into a number when possible.
    """

    if value is None:
        return None

    try:
        return float(value)

    except (ValueError, TypeError):
        return value


# ============================================================
# SELL GRAIN
# ============================================================

def handle_sell(details):
    """
    Create a persistent grain selling request.
    """

    valid, error_message, cleaned = validate_sell_details(details or {})

    if not valid:
        return {
            "success": False,
            "message": error_message,
        }

    request_data = {
        "request_type": "SELL_GRAIN",
        "farmer_name": cleaned["farmer_name"],
        "grain_type": cleaned["grain_type"],
        "quantity": cleaned["quantity"],
        "location": cleaned["location"],
    }

    request = create_request(request_data)

    return {
        "success": True,
        "message": (
            f"Request {request['request_id']} has been created successfully "
            "with status Request Created."
        ),
        "request": request
    }


# ============================================================
# BUY GRAIN
# ============================================================

def handle_buy(details):
    """
    Create a persistent grain buying request.
    """

    valid, error_message, cleaned = validate_buy_details(details or {})

    if not valid:
        return {
            "success": False,
            "message": error_message,
        }

    request_data = {
        "request_type": "BUY_GRAIN",
        "buyer_name": cleaned["buyer_name"],
        "grain_type": cleaned["grain_type"],
        "quantity": cleaned["quantity"],
        "location": cleaned["location"],
    }

    request = create_request(request_data)

    return {
        "success": True,
        "message": (
            f"Request {request['request_id']} has been created successfully "
            "with status Request Created."
        ),
        "request": request
    }


# ============================================================
# CHECK STATUS
# ============================================================

def handle_check_status(details):
    """
    Check the status of a real stored request.
    """

    valid, error_message, cleaned = validate_check_status_details(details or {})

    if not valid:
        return {
            "success": False,
            "message": error_message,
        }

    request_id = cleaned["request_id"]

    request = get_request(request_id)

    if request is None:
        return {
            "success": False,
            "message": (
                "Request not found. Please check the Request ID and try again."
            )
        }

    status = request.get(
        "status",
        "REQUEST_CREATED"
    )
    if status == "REQUEST_CREATED":
        message = f"Request {request['request_id']} has been created successfully."
    else:
        message = (
            f"Request {request['request_id']} is currently "
            f"{status.replace('_', ' ').lower()}."
        )

    return {
        "success": True,
        "message": message,
        "request": request
    }


# ============================================================
# UPDATE STATUS
# ============================================================

def handle_update_status(details):
    """
    Update the status of an existing request.
    """

    request_id = clean_value(
        details.get("request_id")
    )

    new_status = clean_value(
        details.get("status")
    )

    if request_id is None:
        return {
            "success": False,
            "message": "Please provide the request ID."
        }

    if new_status is None:
        return {
            "success": False,
            "message": "Please provide the new status."
        }

    updated_request = update_request_status(
        request_id,
        new_status
    )

    if updated_request is None:
        return {
            "success": False,
            "message": (
                f"Request {request_id} was not found."
            )
        }

    return {
        "success": True,
        "message": (
            f"Request {request_id} status updated to "
            f"{new_status.replace('_', ' ').lower()}."
        ),
        "request": updated_request
    }


# ============================================================
# GET ALL REQUESTS
# ============================================================

def handle_get_all_requests():
    """
    Return all stored requests.
    """

    requests = get_all_requests()

    return {
        "success": True,
        "message": f"{len(requests)} request(s) found.",
        "requests": requests
    }


# ============================================================
# MAIN ACTION ROUTER
# ============================================================

def route_action(intent, details):
    """
    Central action router.

    Supported actions:

        SELL_GRAIN
        BUY_GRAIN
        CHECK_STATUS
        UPDATE_STATUS
        GET_ALL_REQUESTS
    """

    if details is None:
        details = {}

    intent = str(intent).strip().upper()

    # --------------------------------------------------------
    # SELL
    # --------------------------------------------------------

    if intent == "SELL_GRAIN":

        return {
            "action": "SELL_GRAIN",
            "response": handle_sell(details)
        }

    # --------------------------------------------------------
    # BUY
    # --------------------------------------------------------

    elif intent == "BUY_GRAIN":

        return {
            "action": "BUY_GRAIN",
            "response": handle_buy(details)
        }

    # --------------------------------------------------------
    # CHECK STATUS
    # --------------------------------------------------------

    elif intent == "CHECK_STATUS":

        return {
            "action": "CHECK_STATUS",
            "response": handle_check_status(details)
        }

    # --------------------------------------------------------
    # UPDATE STATUS
    # --------------------------------------------------------

    elif intent == "UPDATE_STATUS":

        return {
            "action": "UPDATE_STATUS",
            "response": handle_update_status(details)
        }

    # --------------------------------------------------------
    # GET ALL REQUESTS
    # --------------------------------------------------------

    elif intent == "GET_ALL_REQUESTS":

        return {
            "action": "GET_ALL_REQUESTS",
            "response": handle_get_all_requests()
        }

    # --------------------------------------------------------
    # UNKNOWN ACTION
    # --------------------------------------------------------

    else:

        return {
            "action": "UNKNOWN",
            "response": {
                "success": False,
                "message": (
                    f"I don't know how to handle "
                    f"the action '{intent}'."
                )
            }
        }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n========================================")
    print("     GrainFlow Action Router Test")
    print("========================================\n")

    # --------------------------------------------------------
    # SELL TEST
    # --------------------------------------------------------

    sell_result = route_action(
        "SELL_GRAIN",
        {
            "farmer_name": "Ramesh",
            "grain_type": "tomatoes",
            "quantity": 50,
            "location": "Bhimavaram"
        }
    )

    print("SELL RESULT:")
    print(sell_result)

    # --------------------------------------------------------
    # BUY TEST
    # --------------------------------------------------------

    buy_result = route_action(
        "BUY_GRAIN",
        {
            "buyer_name": "Mithra",
            "grain_type": "dragon fruit",
            "quantity": 20,
            "location": "Hyderabad"
        }
    )

    print("\nBUY RESULT:")
    print(buy_result)

    # --------------------------------------------------------
    # STATUS TEST
    # --------------------------------------------------------

    request_id = sell_result["response"]["request"]["request_id"]

    status_result = route_action(
        "CHECK_STATUS",
        {
            "request_id": request_id
        }
    )

    print("\nSTATUS RESULT:")
    print(status_result)

    print("\n========================================")
    print("      Action Router Test Complete")
    print("========================================")