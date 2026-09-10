import json
import os
from datetime import datetime


# --------------------------------------------------
# FILE LOCATION
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
REQUEST_FILE = os.path.join(DATA_DIR, "requests.json")


# --------------------------------------------------
# INITIAL SETUP
# --------------------------------------------------

def ensure_storage():
    """
    Make sure the data folder and requests.json exist.
    """

    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(REQUEST_FILE):
        with open(REQUEST_FILE, "w", encoding="utf-8") as file:
            json.dump([], file, indent=4)


# --------------------------------------------------
# LOAD REQUESTS
# --------------------------------------------------

def _load_requests():
    """
    Load all requests from requests.json.
    """

    ensure_storage()

    try:
        with open(REQUEST_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except (json.JSONDecodeError, FileNotFoundError):
        return []


# --------------------------------------------------
# SAVE REQUESTS
# --------------------------------------------------

def _save_requests(requests):
    """
    Save all requests to requests.json.
    """

    ensure_storage()

    with open(REQUEST_FILE, "w", encoding="utf-8") as file:
        json.dump(requests, file, indent=4)


# --------------------------------------------------
# GENERATE REQUEST ID
# --------------------------------------------------

def _next_request_id():
    """
    Generate IDs like:

    REQ001
    REQ002
    REQ003
    """

    requests = _load_requests()

    highest_number = 0

    for request in requests:

        request_id = request.get("request_id", "")

        if request_id.startswith("REQ"):

            try:
                number = int(request_id.replace("REQ", ""))

                if number > highest_number:
                    highest_number = number

            except ValueError:
                pass

    next_number = highest_number + 1

    return f"REQ{next_number:03d}"


# --------------------------------------------------
# CREATE REQUEST
# --------------------------------------------------

def create_request(request_data):
    """
    Create and permanently store a new request.
    """

    requests = _load_requests()

    new_request = dict(request_data)

    new_request["request_id"] = _next_request_id()

    new_request["created_at"] = datetime.now().isoformat(
        timespec="seconds"
    )

    new_request["status"] = new_request.get(
        "status",
        "REQUEST_CREATED"
    )

    requests.append(new_request)

    _save_requests(requests)

    return new_request


# --------------------------------------------------
# GET REQUEST
# --------------------------------------------------

def get_request(request_id):
    """
    Find a request using its request ID.
    """

    requests = _load_requests()

    request_id = request_id.strip().upper()

    for request in requests:

        if request.get("request_id", "").upper() == request_id:
            return request

    return None


# --------------------------------------------------
# GET ALL REQUESTS
# --------------------------------------------------

def get_all_requests():
    """
    Return all stored requests.
    """

    return _load_requests()


# --------------------------------------------------
# UPDATE REQUEST STATUS
# --------------------------------------------------

def update_request_status(request_id, new_status):
    """
    Update the status of an existing request.
    """

    from smart_parser import normalize_status, VALID_STATUSES

    normalized_status = normalize_status(new_status)

    if normalized_status not in VALID_STATUSES:
        return None

    requests = _load_requests()

    request_id = request_id.strip().upper()

    for request in requests:

        if request.get("request_id", "").upper() == request_id:

            request["status"] = normalized_status

            request["updated_at"] = datetime.now().isoformat(
                timespec="seconds"
            )

            _save_requests(requests)

            return request

    return None


# --------------------------------------------------
# DELETE REQUEST
# --------------------------------------------------

def delete_request(request_id):
    """
    Delete a request using its request ID.
    """

    requests = _load_requests()

    request_id = request_id.strip().upper()

    updated_requests = []

    deleted = False

    for request in requests:

        if request.get("request_id", "").upper() == request_id:
            deleted = True
        else:
            updated_requests.append(request)

    if deleted:
        _save_requests(updated_requests)

    return deleted


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    print("\n===================================")
    print(" GrainFlow Request Store Test")
    print("===================================\n")

    test_request = create_request({
        "request_type": "SELL_GRAIN",
        "farmer_name": "Test Farmer",
        "grain_type": "tomatoes",
        "quantity": 50,
        "location": "Bhimavaram"
    })

    print("Created Request:")
    print(test_request)

    print("\nAll Requests:")

    for request in get_all_requests():
        print(request)

    print("\nRequest Store is working successfully!")