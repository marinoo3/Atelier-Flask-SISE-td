"""
Database Configuration Module.

This module provides database initialization and session management
for the SQLAlchemy ORM layer using a context manager pattern.

Example:
    >>> from app.config.database import Database
    >>> db = Database()
    >>> db.init_db()
    >>> with db.session() as session:
    ...     patient = Patient(nom="Dupont", gravite="jaune")
    ...     session.add(patient)
    ...     session.commit()
"""

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

# TODO: Importer le Base object depuis le module base

load_dotenv()


class Database:
    """
    Database manager class with context manager support for sessions.

    This class provides a singleton-like pattern for database connections
    and a context manager for safe session handling with automatic
    cleanup on exceptions.

    Attributes:
        db_path (str): Path to the SQLite database file.

    Example:
        >>> db = Database()
        >>> db.init_db()
        >>> with db.session() as session:
        ...     patients = session.query(Patient).all()
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the Database manager.

        Args:
            db_path (str, optional): Path to the SQLite database file.
                If not provided, uses DATABASE_PATH env var or defaults
                to "diagnosys.db".
        """
        # Check if data directory exists, create if not
        self.db_path = db_path or os.getenv("DATABASE_PATH", "data/ragme.db")

        if not os.path.exists(self.db_path):
            data_dir = Path(self.db_path).parent
            data_dir.mkdir(parents=True, exist_ok=True)

        self._engine: Engine | None = None
        self._session_factory: sessionmaker | None = None

    @property
    def engine(self) -> Engine:
        """
        Get or create the SQLAlchemy engine (lazy initialization).

        Returns:
            Engine: SQLAlchemy Engine instance connected to the database.
        """
        if self._engine is None:
            # TODO: instancier l'engine SQLAlchemy
            
        return self._engine

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions.

        Provides a transactional scope around a series of operations.
        Automatically handles commit on success and rollback on exception.

        Yields:
            Session: SQLAlchemy Session instance.

        Raises:
            Exception: Re-raises any exception after rollback.

        Example:
            >>> with db.session() as session:
            ...     Document = Document(title="Example", content="This is an example.")
            ...     session.add(Document)
            ...     session.commit()
        """
        if self._session_factory is None:
            # TODO: instancier le sessionmaker SQLAlchemy

        session = self._session_factory()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def init_db(self):
        """
        Initialize the database and create all tables.

        This method should be called once at application startup
        to ensure all tables are created.

        Example:
            >>> db = Database()
            >>> db.init_db()
        """
        # TODO: Créer la table SQLAlchemy en utilisant Base.metadata.create_all
        


# Default database instance
db = Database()
