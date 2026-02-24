"""
Database Models

Defines the database models for the application.
Includes User model for authentication and ApiKey model for API access.
"""

import secrets
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from database import db


class User(db.Model):
    """
    User model for authentication and API key management.

    Attributes:
        id: Primary key
        username: Unique username for login
        email: User's email address
        password_hash: Hashed password (never store plain passwords!)
        created_at: Account creation timestamp
    """

    # Table name in the database
    __tablename__ = "users"

    # Database columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    api_keys = db.relationship(
        "ApiKey", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, password):
        """
        Hash and store the user's password.
        Uses werkzeug's secure password hashing.

        Args:
            password: Plain text password
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Verify a password against the stored hash.

        Args:
            password: Plain text password to verify

        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """String representation of the user"""
        return f"<User {self.username}>"


class ApiKey(db.Model):
    """
    API Key model for API access management.

    Attributes:
        id: Primary key
        user_id: Foreign key to User
        key: The API key string (format: bonus_...)
        created_at: Key creation timestamp
        is_active: Whether the key is currently active
    """

    # Table name in the database
    __tablename__ = "api_keys"

    # Database columns
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    request_logs = db.relationship(
        "RequestLog", backref="api_key", lazy=True, cascade="all, delete-orphan"
    )

    @staticmethod
    def generate_key():
        """
        Generate a unique API key with the format: bonus_<random_hex>

        Returns:
            str: A unique API key
        """
        # Generate 24 random bytes and convert to hex (48 characters)
        random_part = secrets.token_hex(24)
        return f"bonus_{random_part}"

    def __repr__(self):
        """String representation of the API key"""
        # Only show first 12 characters for security
        key_preview = self.key[:12] + "..." if len(self.key) > 12 else self.key
        status = "active" if self.is_active else "inactive"
        return f"<ApiKey {key_preview} ({status})>"


class RequestLog(db.Model):
    """
    Request Log model for tracking API usage.

    Attributes:
        id: Primary key
        api_key_id: Foreign key to ApiKey
        endpoint: The API endpoint called (e.g., /api/get-user)
        method: HTTP method (GET, POST, PUT, DELETE)
        status_code: HTTP response status code
        timestamp: When the request was made
        ip_address: Client IP address (optional)
    """

    # Table name in the database
    __tablename__ = "request_logs"

    # Database columns
    id = db.Column(db.Integer, primary_key=True)
    api_key_id = db.Column(db.Integer, db.ForeignKey("api_keys.id"), nullable=False)
    endpoint = db.Column(db.String(200), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    status_code = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ip_address = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        """String representation of the request log"""
        return f"<RequestLog {self.method} {self.endpoint} -> {self.status_code}>"


class RequestLogNoAuth(db.Model):
    """
    Request Log model for tracking API usage WITHOUT authentication (by IP).
    Used for the 5 free requests per IP limit.

    Attributes:
        id: Primary key
        ip_address: Client IP address (required for tracking)
        endpoint: The API endpoint called (e.g., /api/get-user)
        method: HTTP method (GET, POST, PUT, DELETE)
        status_code: HTTP response status code
        timestamp: When the request was made
    """

    # Table name in the database
    __tablename__ = "request_logs_no_auth"

    # Database columns
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), nullable=False, index=True)
    endpoint = db.Column(db.String(200), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    status_code = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        """String representation of the request log"""
        return f"<RequestLogNoAuth {self.ip_address} - {self.method} {self.endpoint} -> {self.status_code}>"
