from sys import prefix

from flask import Flask
from api_ecommerce.app.products.routes import products_print
from api_ecommerce.app.auth.routes import auth_print


def create_app():
    app = Flask(__name__)

    app.register_blueprint(products_print, url_prefix="/api/")
    app.register_blueprint(auth_print, url_prefix="/api/auth/")
    return app