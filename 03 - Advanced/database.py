"""
Database Configuration

Simple SQLite database setup using Flask-SQLAlchemy.
This file handles the database initialization and configuration.
"""

import os
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy instance
# This will be initialized with the Flask app later
db = SQLAlchemy()


def init_db(app):
    """
    Initialize the database with the Flask application.

    Args:
        app: Flask application instance
    """
    # Get the absolute path to the 03 - Advanced directory
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Configure SQLite database
    # The database file will be created in the 03 - Advanced folder
    db_path = os.path.join(basedir, "bonus.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    # Disable track modifications to save memory
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize the database with the app
    db.init_app(app)

    # Create all tables
    with app.app_context():
        db.create_all()
        print(f"✅ Database initialized successfully at: {db_path}")
