"""
Authentication Blueprint

This blueprint handles user authentication:
- Registration (create new account)
- Login (authenticate existing user)
- Logout (end session)

TODO: Implement the authentication system following the requirements in the TD document.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import db
from models import User

# Create the blueprint
# url_prefix='/auth' means all routes will start with /auth
auth = Blueprint("auth", __name__, url_prefix="/auth")


# TODO: Implement the /register route (GET and POST)
# - GET: Display the registration form (render_template)
# - POST: Process registration data
#   * Validate all fields are present
#   * Validate password length (minimum 6 characters)
#   * Validate passwords match
#   * Check if username/email already exists
#   * Create new User and save to database
#   * Redirect to login page
# Template: register.html


# TODO: Implement the /login route (GET and POST)
# - GET: Display the login form (render_template)
# - POST: Process login data
#   * Validate username and password are present
#   * Find user in database by username
#   * Verify password (for now, direct comparison - later with check_password())
#   * Create session with user_id and username
#   * Redirect to main.index
# Template: login.html


# TODO: Implement the /logout route (GET only)
# - Clear the session
# - Redirect to login page with a flash message
