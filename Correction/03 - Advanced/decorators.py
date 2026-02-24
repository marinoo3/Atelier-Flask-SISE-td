"""
Custom Decorators

This module contains custom decorators for Flask routes.
Decorators are functions that modify the behavior of other functions.
"""

from functools import wraps
from flask import session, redirect, url_for, jsonify, request, g


def login_required(f):
    """
    Decorator to protect routes that require authentication.

    Usage:
        @app.route('/protected')
        @login_required
        def protected_route():
            return "You are logged in!"

    If the user is not logged in, they will be redirected to the login page.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user_id exists in session
        if "user_id" not in session:
            # If it's an API request, return JSON error
            if request.path.startswith("/api/"):
                return jsonify({"error": "Authentication required"}), 401
            # Otherwise, redirect to login page
            return redirect(url_for("auth.login"))

        # User is authenticated, proceed with the original function
        return f(*args, **kwargs)

    return decorated_function


def require_api_key(f):
    """
    Decorator to protect API routes with flexible rate limiting.

    Usage:
        @app.route('/api/protected')
        @require_api_key
        def protected_api():
            # Access the API key via g.api_key if authenticated
            return jsonify({"message": "Success"})

    The API key should be provided in one of these headers:
    - X-API-Key: bonus_your_key_here
    - Authorization: Bearer bonus_your_key_here

    Rate Limiting:
    - WITHOUT API KEY: 5 free requests per IP address
    - WITH VALID API KEY: Unlimited requests

    This encourages users to create accounts and get API keys for unlimited access.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Import here to avoid circular imports
        from models import ApiKey, RequestLog, RequestLogNoAuth
        from database import db

        # Get API key from headers
        api_key = request.headers.get("X-API-Key")

        # Try Authorization header if X-API-Key not found
        if not api_key:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                api_key = auth_header.replace("Bearer ", "")

        # Get client IP
        client_ip = request.remote_addr

        # CASE 1: No API key provided - Use IP-based rate limiting (5 requests max)
        if not api_key:
            # Check how many requests this IP has made
            ip_request_count = RequestLogNoAuth.query.filter_by(
                ip_address=client_ip
            ).count()

            if ip_request_count >= 5:
                return (
                    jsonify(
                        {
                            "error": "Rate limit exceeded",
                            "message": "You have used all 5 free requests. Create an account and get an API key for unlimited access!",
                            "requests_made": ip_request_count,
                            "limit": 5,
                            "hint": "Visit /auth/register to create an account and /dashboard to get your API key",
                        }
                    ),
                    429,
                )

            # Store IP info in g for logging
            g.client_ip = client_ip
            g.api_key = None
            g.user_id = None

            # Execute the original function
            response = f(*args, **kwargs)

            # Log the request after execution (without auth)
            try:
                # Get status code from response
                if hasattr(response, "status_code"):
                    status_code = response.status_code
                elif isinstance(response, tuple) and len(response) > 1:
                    status_code = response[1]
                else:
                    status_code = 200

                # Create log entry for IP-based request
                log = RequestLogNoAuth(
                    ip_address=client_ip,
                    endpoint=request.path,
                    method=request.method,
                    status_code=status_code,
                )
                db.session.add(log)
                db.session.commit()
            except Exception as e:
                # If logging fails, don't break the request
                print(f"Warning: Failed to log request: {e}")

            return response

        # CASE 2: API key provided - Validate and allow unlimited requests
        # Validate API key in database
        key_obj = ApiKey.query.filter_by(key=api_key).first()

        if not key_obj:
            return jsonify({"error": "Invalid API key"}), 401

        if not key_obj.is_active:
            return jsonify({"error": "API key has been revoked"}), 401

        # Store API key object in g for access in the route
        g.api_key = key_obj
        g.user_id = key_obj.user_id
        g.client_ip = client_ip

        # Execute the original function (NO RATE LIMIT with valid API key!)
        response = f(*args, **kwargs)

        # Log the request after execution
        try:
            # Get status code from response
            if hasattr(response, "status_code"):
                status_code = response.status_code
            elif isinstance(response, tuple) and len(response) > 1:
                status_code = response[1]
            else:
                status_code = 200

            # Create log entry
            log = RequestLog(
                api_key_id=key_obj.id,
                endpoint=request.path,
                method=request.method,
                status_code=status_code,
                ip_address=client_ip,
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            # If logging fails, don't break the request
            print(f"Warning: Failed to log request: {e}")

        return response

    return decorated_function
