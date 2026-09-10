import re

from smart_parser import VALID_STATUSES, normalize_status


REQUEST_ID_PATTERN = re.compile(r"^REQ\d+$", re.IGNORECASE)
PERSON_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z .'-]{1,98}[A-Za-z.'-]$")


def validate_person_name(value, field_label="Name"):
    if value is None:
        return False, f"{field_label} is required."

    name = str(value).strip()

    if len(name) < 2:
        return False, f"{field_label} must be at least 2 characters."

    if not PERSON_NAME_PATTERN.match(name):
        return False, f"{field_label} contains invalid characters."

    return True, name.title()


def validate_product(value):
    if value is None:
        return False, "Product is required."

    product = str(value).strip()

    if len(product) < 2:
        return False, "Product name must be at least 2 characters."

    if len(product) > 120:
        return False, "Product name is too long."

    return True, product


def validate_quantity(value):
    if value is None:
        return False, "Quantity is required."

    try:
        quantity = float(value)
    except (TypeError, ValueError):
        return False, "Quantity must be a valid number."

    if quantity <= 0:
        return False, "Quantity must be greater than zero."

    if quantity.is_integer():
        return True, int(quantity)

    return True, quantity


def validate_location(value):
    if value is None:
        return False, "Location is required."

    location = str(value).strip()

    if len(location) < 2:
        return False, "Location must be at least 2 characters."

    if len(location) > 120:
        return False, "Location is too long."

    return True, location


def validate_request_id(value):
    if value is None:
        return False, "Request ID is required."

    request_id = str(value).strip().upper().replace(" ", "")

    if not REQUEST_ID_PATTERN.match(request_id):
        return False, "Request ID must look like REQ001."

    return True, request_id


def validate_status(value):
    if value is None:
        return False, "Status is required."

    status = normalize_status(value)

    if status not in VALID_STATUSES:
        readable = ", ".join(
            sorted(item.replace("_", " ").title() for item in VALID_STATUSES)
        )
        return False, f"Status must be one of: {readable}."

    return True, status


def validate_sell_details(details):
    errors = []
    cleaned = {}

    ok, result = validate_person_name(details.get("farmer_name"), "Farmer name")
    if ok:
        cleaned["farmer_name"] = result
    else:
        errors.append(result)

    ok, result = validate_product(details.get("grain_type"))
    if ok:
        cleaned["grain_type"] = result
    else:
        errors.append(result)

    ok, result = validate_quantity(details.get("quantity"))
    if ok:
        cleaned["quantity"] = result
    else:
        errors.append(result)

    ok, result = validate_location(details.get("location"))
    if ok:
        cleaned["location"] = result
    else:
        errors.append(result)

    if errors:
        return False, "; ".join(errors), cleaned

    return True, None, cleaned


def validate_buy_details(details):
    errors = []
    cleaned = {}

    buyer_name = details.get("buyer_name") or details.get("farmer_name")
    ok, result = validate_person_name(buyer_name, "Buyer name")
    if ok:
        cleaned["buyer_name"] = result
    else:
        errors.append(result)

    ok, result = validate_product(details.get("grain_type"))
    if ok:
        cleaned["grain_type"] = result
    else:
        errors.append(result)

    ok, result = validate_quantity(details.get("quantity"))
    if ok:
        cleaned["quantity"] = result
    else:
        errors.append(result)

    ok, result = validate_location(details.get("location"))
    if ok:
        cleaned["location"] = result
    else:
        errors.append(result)

    if errors:
        return False, "; ".join(errors), cleaned

    return True, None, cleaned


def validate_check_status_details(details):
    ok, result = validate_request_id(details.get("request_id"))
    if not ok:
        return False, result, {}

    return True, None, {"request_id": result}


def validate_update_status_details(details):
    errors = []
    cleaned = {}

    ok, result = validate_request_id(details.get("request_id"))
    if ok:
        cleaned["request_id"] = result
    else:
        errors.append(result)

    ok, result = validate_status(details.get("status"))
    if ok:
        cleaned["status"] = result
    else:
        errors.append(result)

    if errors:
        return False, "; ".join(errors), cleaned

    return True, None, cleaned
