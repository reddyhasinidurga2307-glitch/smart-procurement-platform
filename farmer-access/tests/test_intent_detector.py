import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "nlp")
    )
)

from intent_detector import detect_intent


# SELL_GRAIN tests
def test_sell_grain():
    assert detect_intent("I want to sell my rice") == "SELL_GRAIN"


def test_natural_sell_request():
    assert detect_intent("I have 500 kg of rice to sell") == "SELL_GRAIN"


# BUY_GRAIN tests
def test_buy_grain():
    assert detect_intent("I want to buy wheat") == "BUY_GRAIN"


def test_purchase_grain():
    assert detect_intent("I need to purchase wheat") == "BUY_GRAIN"


# CHECK_STATUS tests
def test_check_status():
    assert detect_intent("I want to track my order") == "CHECK_STATUS"


def test_request_status():
    assert detect_intent("Where is my request?") == "CHECK_STATUS"


def test_order_progress():
    assert detect_intent("Can I know my order progress?") == "CHECK_STATUS"


# UNKNOWN tests
def test_unknown_request():
    assert detect_intent("Hello, I need some help") == "UNKNOWN"


def test_empty_message():
    assert detect_intent("") == "UNKNOWN"


if __name__ == "__main__":

    test_sell_grain()
    test_natural_sell_request()

    test_buy_grain()
    test_purchase_grain()

    test_check_status()
    test_request_status()
    test_order_progress()

    test_unknown_request()
    test_empty_message()

    print("All intent detection tests passed successfully")