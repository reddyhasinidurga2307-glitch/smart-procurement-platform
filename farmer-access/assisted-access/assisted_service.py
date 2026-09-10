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


# Temporary local farmer database
FARMERS = {}


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
                "Please enter a valid number."
            )


def register_farmer():

    print("\n--- REGISTER FARMER ---")

    farmer_id = get_text_input(
        "Enter Farmer ID: "
    ).upper()

    if farmer_id in FARMERS:

        print(
            "\nFarmer already exists."
        )

        print(FARMERS[farmer_id])

        return

    name = get_text_input(
        "Enter Farmer Name: "
    )

    phone = get_text_input(
        "Enter Phone Number: "
    )

    location = get_text_input(
        "Enter Location: "
    )

    FARMERS[farmer_id] = {
        "farmer_id": farmer_id,
        "name": name,
        "phone": phone,
        "location": location
    }

    print("\nFarmer registered successfully!")

    print(FARMERS[farmer_id])


def search_farmer():

    print("\n--- SEARCH FARMER ---")

    farmer_id = get_text_input(
        "Enter Farmer ID: "
    ).upper()

    farmer = FARMERS.get(
        farmer_id
    )

    if farmer:

        print("\nFarmer found:")

        print(farmer)

    else:

        print(
            "\nFarmer not found."
        )


def get_registered_farmer():

    farmer_id = get_text_input(
        "Enter Farmer ID: "
    ).upper()

    farmer = FARMERS.get(
        farmer_id
    )

    if not farmer:

        print(
            "\nFarmer not found. Please register first."
        )

        return None

    return farmer


def sell_product():

    print("\n--- OPERATOR: SELL PRODUCT ---")

    farmer = get_registered_farmer()

    if farmer is None:

        return

    commodity = get_text_input(
        "Enter product name: "
    )

    quantity = get_quantity()

    location = get_text_input(
        "Enter product location: "
    )

    details = {
        "farmer_name": farmer["name"],
        "grain_type": commodity,
        "quantity": quantity,
        "location": location
    }

    print("\nProcessing farmer request...")

    try:

        result = route_action(
            "SELL_GRAIN",
            details
        )

        print("\nGRAINFLOW RESPONSE:")

        print(result)

    except Exception as error:

        print(
            "\nUnable to process request:"
        )

        print(error)


def buy_product():

    print("\n--- OPERATOR: BUY PRODUCT ---")

    buyer_name = get_text_input(
        "Enter Buyer Name: "
    )

    commodity = get_text_input(
        "Enter product name: "
    )

    quantity = get_quantity()

    location = get_text_input(
        "Enter location: "
    )

    details = {
        "buyer_name": buyer_name,
        "grain_type": commodity,
        "quantity": quantity,
        "location": location
    }

    print("\nProcessing buying request...")

    try:

        result = route_action(
            "BUY_GRAIN",
            details
        )

        print("\nGRAINFLOW RESPONSE:")

        print(result)

    except Exception as error:

        print(
            "\nUnable to process request:"
        )

        print(error)


def check_status():

    print("\n--- CHECK REQUEST STATUS ---")

    request_id = get_text_input(
        "Enter Request ID: "
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


def run_assisted_access():

    print("=" * 60)

    print("GRAINFLOW ASSISTED ACCESS")

    print("CSC | FPO | PACS | VILLAGE OPERATOR")

    print("=" * 60)

    while True:

        print("\nChoose an option:")

        print("1. Register Farmer")

        print("2. Search Farmer")

        print("3. Sell Product for Farmer")

        print("4. Buy Product")

        print("5. Check Request Status")

        print("0. Exit")

        choice = input(
            "\nEnter your choice: "
        ).strip()

        if choice == "1":

            register_farmer()

        elif choice == "2":

            search_farmer()

        elif choice == "3":

            sell_product()

        elif choice == "4":

            buy_product()

        elif choice == "5":

            check_status()

        elif choice == "0":

            print(
                "\nThank you for using GrainFlow Assisted Access."
            )

            break

        else:

            print(
                "\nInvalid option. Please try again."
            )


if __name__ == "__main__":

    run_assisted_access()