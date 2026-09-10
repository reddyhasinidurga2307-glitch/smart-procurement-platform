def create_sell_request(farmer_name, grain_type, quantity, location):

    # Validate the farmer's name
    if not farmer_name:
        return {
            "success": False,
            "message": "Farmer name is required"
        }

    # Validate the grain type
    if not grain_type:
        return {
            "success": False,
            "message": "Grain type is required"
        }

    # Validate the quantity
    if quantity <= 0:
        return {
            "success": False,
            "message": "Quantity must be greater than zero"
        }

    # Validate the location
    if not location:
        return {
            "success": False,
            "message": "Location is required"
        }

    # Create the grain selling request
    sell_request = {
        "farmer_name": farmer_name,
        "grain_type": grain_type,
        "quantity": quantity,
        "location": location,
        "status": "REQUEST_CREATED"
    }

    return {
        "success": True,
        "message": "Grain selling request created successfully",
        "request": sell_request
    }


if __name__ == "__main__":

    result = create_sell_request(
        farmer_name="Ramesh",
        grain_type="Rice",
        quantity=500,
        location="Bhimavaram"
    )

    print(result)
    