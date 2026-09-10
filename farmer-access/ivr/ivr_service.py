import os
import sys


CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

FARMER_ACCESS_DIRECTORY = os.path.abspath(
    os.path.join(CURRENT_DIRECTORY, "..")
)

sys.path.append(
    os.path.join(FARMER_ACCESS_DIRECTORY, "actions")
)

from action_router import route_action


def get_text_input(prompt):

    while True:

        value = input(prompt).strip()

        if value:

            return value

        print("Please enter a valid value.")


def get_quantity():

    while True:

        value = input(
            "Enter quantity in kg: "
        ).strip()

        try:

            quantity = float(value)

            if quantity > 0:

                if quantity.is_integer():

                    return int(quantity)

                return quantity

            print(
                "Quantity must be greater than zero."
            )

        except ValueError:

            print(
                "Please enter a valid numeric quantity."
            )


def sell_commodity():

    print("\n--- SELL PRODUCT ---")

    farmer_name = get_text_input(
        "Enter your name: "
    )

    commodity = get_text_input(
        "Enter product name: "
    )

    quantity = get_quantity()

    location = get_text_input(
        "Enter your location: "
    )

    details = {
        "farmer_name": farmer_name,
        "grain_type": commodity,
        "quantity": quantity,
        "location": location
    }

    print("\nProcessing your selling request...")

    try:

        result = route_action(
            "SELL_GRAIN",
            details
        )

        print("\nGRAINFLOW RESPONSE:")

        print(result)

    except Exception as error:

        print(
            "\nUnable to process your request:"
        )

        print(error)


def buy_commodity():

    print("\n--- BUY PRODUCT ---")

    buyer_name = get_text_input(
        "Enter your name: "
    )

    commodity = get_text_input(
        "Enter product name: "
    )

    quantity = get_quantity()

    location = get_text_input(
        "Enter your location: "
    )

    details = {
        "buyer_name": buyer_name,
        "grain_type": commodity,
        "quantity": quantity,
        "location": location
    }

    print("\nProcessing your buying request...")

    try:

        result = route_action(
            "BUY_GRAIN",
            details
        )

        print("\nGRAINFLOW RESPONSE:")

        print(result)

    except Exception as error:

        print(
            "\nUnable to process your request:"
        )

        print(error)


def check_status():

    print("\n--- CHECK REQUEST STATUS ---")

    request_id = get_text_input(
        "Enter your Request ID: "
    )

    details = {
        "request_id": request_id
    }

    try:

        result = route_action(
            "CHECK_STATUS",
            details
        )

        print("\nGRAINFLOW RESPONSE:")

        print(result)

    except Exception as error:

        print(
            "\nUnable to check status:"
        )

        print(error)


def run_ivr():

    print("=" * 60)

    print("WELCOME TO GRAINFLOW PROCUREMENT SYSTEM")

    print("=" * 60)

    while True:

        print("\nPlease choose an option:")

        print("1. Sell a product")

        print("2. Buy a product")

        print("3. Check request status")

        print("0. Exit")

        choice = input(
            "\nEnter your choice: "
        ).strip()

        if choice == "1":

            sell_commodity()

        elif choice == "2":

            buy_commodity()

        elif choice == "3":

            check_status()

        elif choice == "0":

            print(
                "\nThank you for using GrainFlow."
            )

            break

        else:

            print(
                "\nInvalid choice. Please try again."
            )


if __name__ == "__main__":

    run_ivr()