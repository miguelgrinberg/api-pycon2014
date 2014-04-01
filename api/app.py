import os
from flask import Flask
from .models import db


def create_app(config_module=None):
    app = Flask(__name__)
    app.config.from_object(config_module or
                           os.environ.get('FLASK_CONFIG') or
                           'config')

    db.init_app(app)

    from api.v1_0 import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1.0')

    if app.config['USE_TOKEN_AUTH']:
        from api.token import token as token_blueprint
        app.register_blueprint(token_blueprint, url_prefix='/auth')
    return app

