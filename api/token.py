from flask import Blueprint, jsonify, g
from flask.ext.httpauth import HTTPBasicAuth
from .models import User
from .errors import unauthorized
from .decorators import no_cache

token = Blueprint('token', __name__)
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username_or_token, password):
    g.user = User.query.filter_by(username=username_or_token).first()
    if not g.user:
        return False
    return g.user.verify_password(password)


@auth.error_handler
def unauthorized_error():
    return unauthorized('Please authenticate to access this API')


@token.route('/request-token')
@no_cache
@auth.login_required
def request_token():
    return jsonify({'token': g.user.generate_auth_token()})
