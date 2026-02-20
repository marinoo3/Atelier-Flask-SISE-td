"""
Main Routes Blueprint

Contains the main pages of the application (index, dashboard, test pages).
Separate from API routes for better organization.
"""

from flask import Blueprint, render_template, session, redirect, url_for, flash
from sqlalchemy.sql import func

# TODO: Import the login_required decorator once implemented
# from decorators import login_required
from models import User, ApiKey, RequestLog
from database import db

# Create blueprint without prefix (for root routes)
main = Blueprint("main", __name__)


@main.route("/")
def index():
    """Bonus main page - shows API test interface"""
    return render_template("bonus.html")


@main.route("/dashboard")
# TODO: Add @login_required decorator to protect this route
def dashboard():
    """
    Protected dashboard - only accessible to logged-in users.
    TODO: Add the @login_required decorator once implemented.
    """
    # Get current user from session
    user = User.query.get(session["user_id"])

    if not user:
        return "User not found", 404

    # Format created_at date
    created_at = user.created_at.strftime("%Y-%m-%d")

    # Get user's API keys (active ones first)
    api_keys = (
        ApiKey.query.filter_by(user_id=user.id)
        .order_by(ApiKey.is_active.desc(), ApiKey.created_at.desc())
        .all()
    )

    # Calculate request counts for each API key
    api_keys_with_counts = []
    for key in api_keys:
        request_count = RequestLog.query.filter_by(api_key_id=key.id).count()
        api_keys_with_counts.append(
            {
                "key": key,
                "request_count": request_count,
                "requests_remaining": max(0, 15 - request_count),
            }
        )

    # Calculate request statistics by route (endpoint)
    # Get all API keys IDs for this user
    user_key_ids = [key.id for key in api_keys]

    # Query to group by endpoint and count requests
    route_stats = (
        db.session.query(
            RequestLog.endpoint,
            RequestLog.method,
            func.count(RequestLog.id).label("count"),
        )
        .filter(RequestLog.api_key_id.in_(user_key_ids))
        .group_by(RequestLog.endpoint, RequestLog.method)
        .order_by(func.count(RequestLog.id).desc())
        .all()
    )

    # Format route stats for template
    route_statistics = [
        {"endpoint": stat.endpoint, "method": stat.method, "count": stat.count}
        for stat in route_stats
    ]

    return render_template(
        "dashboard.html",
        user=user,
        created_at=created_at,
        api_keys_with_counts=api_keys_with_counts,
        route_statistics=route_statistics,
    )


@main.route("/test-db")
# TODO: Add @login_required decorator to protect this route
def test_db():
    """Test page to verify database functionality (should be protected)"""
    # Count users in database
    user_count = User.query.count()

    # Get all users
    users = User.query.all()

    return render_template("test_db.html", user_count=user_count, users=users)


@main.route("/api-keys/generate", methods=["POST"])
# TODO: Add @login_required decorator to protect this route
def generate_api_key():
    """
    Generate a new API key for the current user.
    Protected route - requires authentication.
    """
    # Check if user already has an active API key (limit to 1 for this bonus)
    existing_key = ApiKey.query.filter_by(
        user_id=session["user_id"], is_active=True
    ).first()

    if existing_key:
        flash(
            "You already have an active API key. Revoke it first to generate a new one.",
            "error",
        )
        return redirect(url_for("main.dashboard"))

    # Generate new API key
    new_key = ApiKey(user_id=session["user_id"], key=ApiKey.generate_key())

    db.session.add(new_key)
    db.session.commit()

    flash(f"API key generated successfully: {new_key.key}", "success")
    return redirect(url_for("main.dashboard"))


@main.route("/api-keys/<int:key_id>/revoke", methods=["POST"])
# TODO: Add @login_required decorator to protect this route
def revoke_api_key(key_id):
    """
    Revoke (deactivate) an API key.
    Protected route - requires authentication.
    """
    # Get the API key
    api_key = ApiKey.query.get_or_404(key_id)

    # Check if the key belongs to the current user
    if api_key.user_id != session["user_id"]:
        flash("You don't have permission to revoke this key", "error")
        return redirect(url_for("main.dashboard"))

    # Revoke the key
    api_key.is_active = False
    db.session.commit()

    flash("API key revoked successfully", "info")
    return redirect(url_for("main.dashboard"))


@main.route("/account/delete", methods=["POST"])
# TODO: Add @login_required decorator to protect this route
def delete_account():
    """
    Delete the current user's account and all associated data.
    Protected route - requires authentication.

    WARNING: This action is permanent and cannot be undone!
    Deletes:
    - All API keys
    - All request logs
    - User account
    """
    user_id = session["user_id"]

    # Get user
    user = User.query.get_or_404(user_id)

    # Get all API keys for this user
    api_keys = ApiKey.query.filter_by(user_id=user_id).all()

    # Delete all request logs for each API key
    for api_key in api_keys:
        RequestLog.query.filter_by(api_key_id=api_key.id).delete()

    # Delete all API keys
    ApiKey.query.filter_by(user_id=user_id).delete()

    # Delete the user
    username = user.username  # Save for flash message
    db.session.delete(user)
    db.session.commit()

    # Logout (clear session)
    session.clear()

    flash(f"Account '{username}' has been permanently deleted. Goodbye!", "success")
    return redirect(url_for("main.index"))
