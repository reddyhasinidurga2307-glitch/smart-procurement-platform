def check_request_status(request_id):

    # Sample requests for testing
    requests = {
        "REQ001": {
            "status": "REQUEST_CREATED",
            "message": "Your grain request has been created successfully"
        },
        "REQ002": {
            "status": "IN_PROGRESS",
            "message": "Your grain request is currently being processed"
        },
        "REQ003": {
            "status": "COMPLETED",
            "message": "Your grain request has been completed successfully"
        }
    }

    # Check whether the request exists
    if not request_id:
        return {
            "success": False,
            "message": "Request ID is required"
        }

    # Return the request status
    if request_id in requests:
        return {
            "success": True,
            "request_id": request_id,
            "status": requests[request_id]["status"],
            "message": requests[request_id]["message"]
        }

    # Handle invalid request ID
    return {
        "success": False,
        "request_id": request_id,
        "message": "Request not found"
    }


if __name__ == "__main__":

    test_request_ids = [
        "REQ001",
        "REQ002",
        "REQ003",
        "REQ999"
    ]

    for request_id in test_request_ids:
        result = check_request_status(request_id)
        print(result)