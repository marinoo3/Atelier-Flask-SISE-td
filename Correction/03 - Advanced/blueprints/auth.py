"""
Authentication Blueprint

This blueprint handles user authentication:
- Registration (create new account)
- Login (authenticate existing user)
- Logout (end session)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import db
from models import User

# Create the blueprint
# url_prefix='/auth' means all routes will start with /auth
auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route("/register", methods=["GET", "POST"])
def register():
    """
    User registration page.

    GET: Display registration form
    POST: Process registration and create new user
    """
    if request.method == "POST":
        # Get form data
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        password_confirm = request.form.get("password_confirm")

        # Validation
        if not username or not email or not password:
            flash("All fields are required", "error")
            return render_template("register.html")

        if password != password_confirm:
            flash("Passwords do not match", "error")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters", "error")
            return render_template("register.html")

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists", "error")
            return render_template("register.html")

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash("Email already registered", "error")
            return render_template("register.html")

        # Create new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)  # Hash the password

        # Add to database
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("auth.login"))

    # GET request - show form
    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    """
    User login page.

    GET: Display login form
    POST: Authenticate user and create session
    """
    if request.method == "POST":
        # Get form data
        username = request.form.get("username")
        password = request.form.get("password")

        # Validation
        if not username or not password:
            flash("Username and password are required", "error")
            return render_template("login.html")

        # Find user in database
        user = User.query.filter_by(username=username).first()

        # Check if user exists and password is correct
        if user and user.check_password(password):
            # Create session
            session["user_id"] = user.id
            session["username"] = user.username

            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("main.index"))
        else:
            flash("Invalid username or password", "error")
            return render_template("login.html")

    # GET request - show form
    return render_template("login.html")


@auth.route("/logout")
def logout():
    """
    Logout user by clearing the session.
    """
    # Clear session data
    session.clear()

    flash("You have been logged out", "info")
    return redirect(url_for("auth.login"))
