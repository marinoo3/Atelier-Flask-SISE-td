"""
Flask Bonus Application

Bonus application to test Flask features - TD Project.
Demonstrates Flask concepts: blueprints, authentication, decorators, API routes.

Usage:
    uv run python run.py

Architecture:
    - 03 - Advanced/blueprints/auth.py: Authentication routes (register, login, logout)
    - 03 - Advanced/blueprints/main_routes.py: Main pages (index, dashboard, test-db)
    - 03 - Advanced/blueprints/bonus_routes.py: API routes for testing
    - 03 - Advanced/decorators.py: Custom decorators (@login_required)
    - 03 - Advanced/models.py: Database models (User)
"""

from flask import Flask, jsonify

# Import database setup
from database import init_db

# Import models (ensures they are registered with SQLAlchemy)
import models  # noqa: F401

# Import blueprints
from blueprints.auth import auth
from blueprints.main_routes import main
from blueprints.bonus_routes import bonus, ROUTES_METADATA


app = Flask(__name__, template_folder="templates", static_folder="static")

# Configuration
app.config["DEBUG"] = True
app.config["JSON_AS_ASCII"] = False  # To support French characters
app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"  # For sessions

# Initialize database
init_db(app)

# Register blueprints
app.register_blueprint(auth)  # /auth/*
app.register_blueprint(main)  # /, /dashboard, /test-db
app.register_blueprint(bonus)  # /api/*


# ============================================================================
# ERROR HANDLERS
# ============================================================================


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return (
        jsonify({"status": "error", "message": "Route not found", "error": str(error)}),
        404,
    )


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return (
        jsonify(
            {
                "status": "error",
                "message": "Internal server error",
                "error": str(error),
            }
        ),
        500,
    )


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Flask Bonus Application - TD Project")
    print("=" * 60)
    print("📍 Server: http://localhost:5000")
    print("📝 Test interface: http://localhost:5000")
    print("🔐 Login: http://localhost:5000/auth/login")
    print("📊 Dashboard: http://localhost:5000/dashboard")
    print()
    print("Available API routes:")
    for key, route in ROUTES_METADATA.items():
        method = route["methods"][0]
        print(f"  • {method:6} {route['path']:30} - {route['description']}")
    print("=" * 60)
    print()

    app.run(host="0.0.0.0", port=5000, debug=True)
