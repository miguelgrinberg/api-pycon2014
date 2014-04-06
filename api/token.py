from flask import Blueprint, jsonify, g
from flask.ext.httpauth import HTTPBasicAuth
from .models import User
from .errors import unauthorized
from .decorators import no_cache, json

token = Blueprint('token', __name__)
token_auth = HTTPBasicAuth()


@token_auth.verify_password
def verify_password(username_or_token, password):
    g.user = User.query.filter_by(username=username_or_token).first()
    if not g.user:
        return False
    return g.user.verify_password(password)


@token_auth.error_handler
def unauthorized_error():
    return unauthorized('Please authenticate to access this API')


@token.route('/request-token')
@no_cache
@token_auth.login_required
@json
def request_token():
    return {'token': g.user.generate_auth_token()}
