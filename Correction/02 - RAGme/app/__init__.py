from flask import Flask

from app.database.sql_db import db
from app.services import RagService, DocumentService


class AppContext(Flask):
    rag_service: RagService
    document_service: DocumentService


def create_app() -> Flask:
    """
    Create Flask app instance with context and load blueprints

    Returns:
        Flask: App instance
    """
    # Create Flask app
    app = Flask(__name__)

    # Load configuration
    with app.app_context():
        app.rag_service = RagService()
        app.document_service = DocumentService()

    db.init_db()

    # Init routes pages
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Init ajax backend
    from app.ajax import ajax as ajax_blueprint
    app.register_blueprint(ajax_blueprint, url_prefix="/ajax")

    return app