from flask import Flask

# from app.module import object


class AppContext(Flask):
    # my_service: MyService
    pass


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
        # app.my_service = MyService()
        pass

    # Init routes pages
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Init ajax backend
    from app.ajax import ajax as ajax_blueprint
    app.register_blueprint(ajax_blueprint, url_prefix="/ajax")

    return app