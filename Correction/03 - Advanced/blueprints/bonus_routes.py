"""
Bonus Routes Blueprint

Contains all the bonus API routes for testing Flask features.
This organization allows for better code structure and separation of concerns.
Most routes are protected with @require_api_key decorator for rate limiting.
"""

import time
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from decorators import require_api_key

# Create blueprint
bonus = Blueprint("bonus", __name__, url_prefix="/api")


# ============================================================================
# ROUTES METADATA - Define metadata for each test route
# ============================================================================

ROUTES_METADATA = {
    "get-user": {
        "path": "/api/get-user/123",
        "methods": ["GET"],
        "description": "Get user details by ID",
        "protected": True,
        "params": [
            {
                "name": "user_id",
                "type": "integer",
                "required": True,
                "description": "User ID to retrieve (in URL)",
            }
        ],
        "body_example": None,
    },
    "post-user": {
        "path": "/api/post-user",
        "methods": ["POST"],
        "description": "Create a new user with JSON data",
        "protected": True,
        "params": [],
        "body_example": {
            "name": "John Doe",
            "email": "john.doe@example.com",
        },
    },
    "put-user": {
        "path": "/api/put-user/123",
        "methods": ["PUT"],
        "description": "Update a user",
        "protected": True,
        "params": [
            {
                "name": "user_id",
                "type": "integer",
                "required": True,
                "description": "User ID to modify (in URL)",
            }
        ],
        "body_example": {
            "name": "New user",
            "description": "Updated description",
        },
    },
    "delete-user": {
        "path": "/api/delete-user/456",
        "methods": ["DELETE"],
        "description": "Delete a user",
        "protected": True,
        "params": [
            {
                "name": "user_id",
                "type": "integer",
                "required": True,
                "description": "User ID to delete (in URL)",
            }
        ],
        "body_example": None,
    },
    "error-example": {
        "path": "/api/error-example",
        "methods": ["GET"],
        "description": "Error handling test",
        "protected": True,
        "params": [
            {
                "name": "type",
                "type": "string",
                "required": False,
                "default": "500",
                "description": "Error type (400, 403, 404, 500)",
            }
        ],
        "body_example": None,
    },
    "request-info": {
        "path": "/api/request-info",
        "methods": ["GET"],
        "description": "Get detailed information about the current request",
        "protected": True,
        "params": [],
        "body_example": None,
    },
}


# ============================================================================
# API ROUTES
# ============================================================================


@bonus.route("/routes", methods=["GET"])
def get_routes():
    """Returns the list of all available routes with their metadata"""
    return jsonify({"status": "success", "routes": ROUTES_METADATA})


@bonus.route("/get-user/<int:user_id>", methods=["GET"])
@require_api_key
def get_user(user_id):
    """Example of GET route with URL parameter (protected with API key)"""
    user_data = {
        "id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com",
        "created_at": datetime.now().isoformat(),
    }

    return jsonify({"status": "success", "data": user_data})


@bonus.route("/post-user", methods=["POST"])
@require_api_key
def post_user():
    """Example of POST route with JSON data (protected with API key)"""
    data = request.get_json()

    if not data or "name" not in data or "email" not in data:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    new_user = {
        "id": 123,  # Fake ID for bonus
        "name": data["name"],
        "email": data["email"],
        "created_at": datetime.now().isoformat(),
    }

    return jsonify({"status": "success", "data": new_user}), 201


@bonus.route("/put-user/<int:user_id>", methods=["PUT"])
@require_api_key
def put_user(user_id):
    """Example of PUT route for updating a user (protected with API key)"""
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    updated_user = {
        "id": user_id,
        "name": data.get("name", f"User {user_id}"),
        "description": data.get("description", "No description"),
        "updated_at": datetime.now().isoformat(),
    }

    return jsonify({"status": "success", "data": updated_user})


@bonus.route("/delete-user/<int:user_id>", methods=["DELETE"])
@require_api_key
def delete_user(user_id):
    """Example of DELETE route for deleting a user (protected with API key)"""
    return jsonify({"status": "success", "message": f"User {user_id} deleted"})


@bonus.route("/error-example", methods=["GET"])
@require_api_key
def error_example():
    """Example of error handling (protected with API key)"""
    error_type = request.args.get("type", "500")

    if error_type == "404":
        return jsonify({"status": "error", "message": "Resource not found"}), 404
    elif error_type == "403":
        return jsonify({"status": "error", "message": "Access forbidden"}), 403
    elif error_type == "400":
        return jsonify({"status": "error", "message": "Bad request"}), 400
    else:
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@bonus.route("/request-info", methods=["GET"])
@require_api_key
def request_info():
    """
    Returns detailed information about the current HTTP request.
    Demonstrates access to Flask's request object and global context (g).

    Protected with API key for rate limiting.
    """

    # Get timing information
    request_start = time.time()

    # Build request information
    info = {
        "status": "success",
        "request": {
            "method": request.method,
            "url": request.url,
            "path": request.path,
            "endpoint": request.endpoint,
            "remote_addr": request.remote_addr,
            "scheme": request.scheme,  # http or https
            "is_secure": request.is_secure,
        },
        "headers": dict(request.headers),
        "args": dict(request.args),  # Query parameters
        "authentication": {
            "has_api_key": hasattr(g, "api_key") and g.api_key is not None,
            "user_id": g.user_id if hasattr(g, "user_id") else None,
            "client_ip": g.client_ip if hasattr(g, "client_ip") else None,
        },
        "server": {
            "host": request.host,
            "host_url": request.host_url,
        },
        "timing": {
            "request_time": datetime.now().isoformat(),
            "processing_time_ms": round((time.time() - request_start) * 1000, 2),
        },
    }

    return jsonify(info)
