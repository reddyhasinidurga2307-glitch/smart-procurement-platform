import re


# ============================================================
# VALID STATUSES
# ============================================================

VALID_STATUSES = {
    "REQUEST_CREATED",
    "UNDER_REVIEW",
    "MATCHED",
    "NEGOTIATION",
    "COMPLETED",
    "CANCELLED",
    "REJECTED",
}

STATUS_ALIASES = {
    "REQUEST CREATED": "REQUEST_CREATED",
    "UNDER REVIEW": "UNDER_REVIEW",
    "IN REVIEW": "UNDER_REVIEW",
    "MATCHED": "MATCHED",
    "NEGOTIATION": "NEGOTIATION",
    "COMPLETED": "COMPLETED",
    "CANCELLED": "CANCELLED",
    "REJECTED": "REJECTED",
}


def normalize_status(value):
    """Normalize free-text status values to canonical codes."""

    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    upper = text.upper().replace("-", "_")
    upper_spaced = text.upper().replace("_", " ").strip()

    if upper in VALID_STATUSES:
        return upper

    if upper_spaced in STATUS_ALIASES:
        return STATUS_ALIASES[upper_spaced]

    compact = upper_spaced.replace(" ", "_")
    if compact in VALID_STATUSES:
        return compact

    return compact


# ============================================================
# BASIC CLEANING
# ============================================================

def clean_text(text):
    if not text:
        return ""

    text = str(text).strip()
    text = re.sub(r"\s+", " ", text)

    return text


def normalize_text(text):
    return clean_text(text).lower()


# ============================================================
# QUANTITY EXTRACTION
# ============================================================

def extract_quantity(text):
    text = clean_text(text)

    patterns = [
        r"\b(\d+(?:\.\d+)?)\s*(?:kg|kgs|kilogram|kilograms)\b",
        r"\b(\d+(?:\.\d+)?)\s*(?:ton|tons|tonne|tonnes)\b",
        r"\b(\d+(?:\.\d+)?)\s*(?:quintal|quintals)\b",
        r"\bquantity\s*(?:is|of)?\s*(\d+(?:\.\d+)?)\b",
        r"\bqty\s*(?:is|of)?\s*(\d+(?:\.\d+)?)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None

    return None


# ============================================================
# REQUEST ID EXTRACTION
# ============================================================

def extract_request_id(text):
    text = clean_text(text)

    match = re.search(
        r"\bREQ\d+\b",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(0).upper()

    return None


# ============================================================
# STATUS EXTRACTION
# ============================================================

def extract_status(text):
    text = clean_text(text)

    # Direct status matching.
    # Sort by length so longer statuses are checked first.
    statuses = sorted(
        VALID_STATUSES,
        key=len,
        reverse=True
    )

    for status in statuses:
        pattern = rf"\b{re.escape(status)}\b"

        if re.search(pattern, text, re.IGNORECASE):
            return status

    # Support natural-language versions
    # such as "under review".
    natural_statuses = {
        "UNDER REVIEW": "UNDER_REVIEW",
        "REQUEST CREATED": "REQUEST_CREATED",
        "IN REVIEW": "UNDER_REVIEW",
    }

    for phrase, status in natural_statuses.items():
        pattern = rf"\b{re.escape(phrase)}\b"

        if re.search(pattern, text, re.IGNORECASE):
            return status

    return None


# ============================================================
# PERSON NAME EXTRACTION
# ============================================================

def extract_person_name(text):
    text = clean_text(text)

    patterns = [
        r"\bmy name is\s+([A-Za-z]+(?:\s+[A-Za-z]+){0,2})",
        r"\bname is\s+([A-Za-z]+(?:\s+[A-Za-z]+){0,2})",
        r"\bi am\s+([A-Za-z]+(?:\s+[A-Za-z]+){0,2})",
        r"\bi'm\s+([A-Za-z]+(?:\s+[A-Za-z]+){0,2})",
    ]

    stop_words = {
        "from",
        "at",
        "in",
        "with",
        "and",
        "want",
        "would",
        "like",
        "to",
        "selling",
        "buying",
    }

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            name = match.group(1).strip()

            words = name.split()

            while words and words[-1].lower() in stop_words:
                words.pop()

            if words:
                return " ".join(words)

    return None


# ============================================================
# LOCATION EXTRACTION
# ============================================================

def extract_location(text):
    text = clean_text(text)

    patterns = [
        r"\bfrom\s+(.+?)(?=\s+(?:my name is|name is|i am|i'm)\b|$)",
        r"\bat\s+(.+?)(?=\s+(?:my name is|name is|i am|i'm)\b|$)",
        r"\bin\s+(.+?)(?=\s+(?:my name is|name is|i am|i'm)\b|$)",
        r"\blocation\s*(?:is|:)?\s*(.+?)(?=\s+(?:my name is|name is|i am|i'm)\b|$)",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            location = match.group(1).strip()

            location = re.sub(
                r"[,.!?]+$",
                "",
                location
            ).strip()

            location = re.sub(
                r"\s+(?:my name is|name is|i am|i'm)\b.*$",
                "",
                location,
                flags=re.IGNORECASE,
            ).strip()

            if location:
                return location

    return None


# ============================================================
# PRODUCT / GRAIN EXTRACTION
# ============================================================

UNIT_PATTERN = (
    r"(?:kg|kgs|kilogram|kilograms|ton|tons|tonne|tonnes|"
    r"quintal|quintals)"
)

BOUNDARY = r"(?=\s+(?:from|at|in|my name is|name is|i am|i'm)\b|$)"


def sanitize_product(product):
    """Clean and validate extracted product names."""

    if not product:
        return None

    product = clean_text(product)
    product = re.sub(r"[,.!?]+$", "", product).strip()

    # Remove accidental trailing name/location fragments.
    product = re.sub(
        r"\s+(?:my name is|name is|i am|i'm)\b.*$",
        "",
        product,
        flags=re.IGNORECASE,
    ).strip()

    # Fix malformed captures such as "s of tomatoes".
    malformed = re.match(
        r"^[a-z]\s+of\s+(.+)$",
        product,
        re.IGNORECASE,
    )
    if malformed:
        product = malformed.group(1).strip()

    if len(product) < 2:
        return None

    if re.fullmatch(r"[a-z]\s+of", product, re.IGNORECASE):
        return None

    return product


def extract_product(text):
    text = clean_text(text)

    patterns = [
        # sell / buy with quantity + unit + of product
        rf"\b(?:want to\s+)?(?:sell|selling)\s+\d+(?:\.\d+)?\s*"
        rf"{UNIT_PATTERN}\s+of\s+(.+?){BOUNDARY}",

        rf"\b(?:want to\s+)?(?:buy|buying)\s+\d+(?:\.\d+)?\s*"
        rf"{UNIT_PATTERN}\s+of\s+(.+?){BOUNDARY}",

        # Generic: 50 kg of tomatoes
        rf"\b\d+(?:\.\d+)?\s*{UNIT_PATTERN}\s+of\s+(.+?){BOUNDARY}",

        # Natural phrasing without the optional "of".
        rf"\b(?:want to\s+)?(?:sell|selling|buy|buying)\s+\d+(?:\.\d+)?\s*"
        rf"{UNIT_PATTERN}\s+(.+?){BOUNDARY}",

        rf"\b\d+(?:\.\d+)?\s*{UNIT_PATTERN}\s+(.+?){BOUNDARY}",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            product = sanitize_product(match.group(1))

            if product:
                return product

    return None


# ============================================================
# INTENT DETECTION
# ============================================================

def detect_intent(text):
    normalized = normalize_text(text)

    # EXIT
    if normalized in {
        "exit",
        "quit",
        "bye",
        "stop",
    }:
        return "EXIT"

    # RESET
    if normalized in {
        "reset",
        "start over",
        "restart",
    }:
        return "RESET"

    # UPDATE STATUS
    update_patterns = [
        r"\bupdate\s+(?:the\s+)?status\b",
        r"\bchange\s+(?:the\s+)?status\b",
        r"\bmark\s+req\d+\b.*\b(?:as|to)\b",
        r"\breq\d+\s+to\s+\w+",
    ]

    for pattern in update_patterns:
        if re.search(pattern, normalized):
            return "UPDATE_STATUS"

    # CHECK STATUS
    if (
        re.search(r"\bstatus\s+req\d+\b", normalized)
        or re.search(r"\bcheck\s+(?:the\s+)?status\b", normalized)
        or re.search(r"\btrack\s+req\d+\b", normalized)
    ):
        return "CHECK_STATUS"

    # GET ALL REQUESTS
    if (
        "all requests" in normalized
        or "show requests" in normalized
        or "show all requests" in normalized
        or "list requests" in normalized
    ):
        return "GET_ALL_REQUESTS"

    # SELL
    if re.search(
        r"\b(?:sell|selling)\b",
        normalized
    ):
        return "SELL_GRAIN"

    # BUY
    if re.search(
        r"\b(?:buy|buying)\b",
        normalized
    ):
        return "BUY_GRAIN"

    return "UNKNOWN"


# ============================================================
# MAIN SMART PARSER
# ============================================================

def smart_parse(text):
    text = clean_text(text)

    intent = detect_intent(text)

    details = {
        "farmer_name": None,
        "buyer_name": None,
        "grain_type": None,
        "quantity": None,
        "location": None,
    }

    # --------------------------------------------------------
    # SELL / BUY
    # --------------------------------------------------------

    if intent in {
        "SELL_GRAIN",
        "BUY_GRAIN",
    }:
        person_name = extract_person_name(text)
        product = extract_product(text)
        quantity = extract_quantity(text)
        location = extract_location(text)

        details["grain_type"] = product
        details["quantity"] = quantity
        details["location"] = location

        if intent == "SELL_GRAIN":
            details["farmer_name"] = person_name
            details["buyer_name"] = person_name

        elif intent == "BUY_GRAIN":
            details["farmer_name"] = person_name
            details["buyer_name"] = person_name

    # --------------------------------------------------------
    # UPDATE STATUS
    # --------------------------------------------------------

    elif intent == "UPDATE_STATUS":
        return {
            "intent": "UPDATE_STATUS",
            "details": {
                "request_id": extract_request_id(text),
                "status": extract_status(text),
            },
        }

    # --------------------------------------------------------
    # CHECK STATUS
    # --------------------------------------------------------

    elif intent == "CHECK_STATUS":
        return {
            "intent": "CHECK_STATUS",
            "details": {
                "request_id": extract_request_id(text),
            },
        }

    # --------------------------------------------------------
    # OTHER INTENTS
    # --------------------------------------------------------

    elif intent in {
        "RESET",
        "EXIT",
        "GET_ALL_REQUESTS",
    }:
        return {
            "intent": intent,
            "details": {},
        }

    return {
        "intent": intent,
        "details": details,
    }


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

def smart_parse_message(text):
    return smart_parse(text)


def smart_parse_request(text):
    return smart_parse(text)


def understand_message(text):
    return smart_parse(text)


# ============================================================
# SELF TEST
# ============================================================

if __name__ == "__main__":

    test_messages = [
        "I want to sell 50 kg of tomatoes",

        "I want to sell 50 kgs of tomatoes from Bhimavaram my name is Mishra",

        "I want to buy 100 kg of red chillie",

        "I want to buy 100 kg of tomatoes from Bhimavaram my name is Mishra",

        "I want to sell 20 kilograms of apples from Bhimavaram my name is Poorna",

        "I want to sell 30 kgs of green chillies from Srikakulam my name is Mithra",

        "Update status of REQ004 to UNDER_REVIEW",

        "Update status of REQ004 to MATCHED",

        "Change status of REQ004 to COMPLETED",

        "Mark REQ004 as NEGOTIATION",

        "REQ004 to COMPLETED",

        "status REQ004",

        "reset",

        "exit",
    ]

    print("=" * 70)
    print("SMART PARSER TEST")
    print("=" * 70)

    for message in test_messages:

        result = smart_parse(message)

        print()
        print("INPUT :", message)
        print("OUTPUT:", result)

    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)