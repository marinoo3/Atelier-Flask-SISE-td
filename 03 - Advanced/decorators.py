"""
Custom Decorators

This module contains custom decorators for Flask routes.
Decorators are functions that modify the behavior of other functions.
"""

from functools import wraps
from flask import session, redirect, url_for, jsonify, request, g


# TODO: Implement the @login_required decorator
# This decorator should protect routes that require authentication.
#
# Requirements:
# 1. Use @wraps(f) to preserve the original function name
# 2. Check if "user_id" exists in session
# 3. If not authenticated:
#    - For API routes (request.path.startswith("/api/")): return JSON error 401
#    - For web routes: redirect to auth.login
# 4. If authenticated: proceed with the original function
#
# Usage example:
#     @app.route('/dashboard')
#     @login_required
#     def dashboard():
#         return "Protected page"
#
# Hint: Look at the @require_api_key decorator below for inspiration on structure


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
