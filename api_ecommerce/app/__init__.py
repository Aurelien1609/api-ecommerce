from flask import Flask, g
from api_ecommerce.app.products.routes import products_print
from api_ecommerce.app.auth.routes import auth_print
from api_ecommerce.app.commands.routes import commands_print
from api_ecommerce.models import build_engine
from api_ecommerce.config import DATABASE_SQL
from sqlalchemy.orm import sessionmaker


def create_app():
    app = Flask(__name__)

    app.register_blueprint(products_print, url_prefix="/api/")
    app.register_blueprint(auth_print, url_prefix="/api/auth/")
    app.register_blueprint(commands_print, url_prefix="/api/")
    app.session_factory = sessionmaker(bind=build_engine(DATABASE_SQL)[0])

    def inject_session():
        if not hasattr(g, "db_session"):
            session_factory = getattr(app, "session_factory", None)
            if session_factory is not None:
                g.db_session = session_factory()

    app.before_request(inject_session)
    return app