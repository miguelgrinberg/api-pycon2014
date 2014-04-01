from flask import jsonify


class ValidationError(ValueError):
    pass


def not_modified():
    response = jsonify({'status': 304, 'error': 'not modified'})
    response.status_code = 304
    return response


def bad_request(message):
    response = jsonify({'status': 400, 'error': 'bad request',
                        'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'status': 401, 'error': 'unauthorized',
                        'message': message})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({'status': 403, 'error': 'forbidden',
                        'message': message})
    response.status_code = 403
    return response


def not_found(message):
    response = jsonify({'status': 404, 'error': 'not found',
                        'message': message})
    response.status_code = 404
    return response


def precondition_failed():
    response = jsonify({'status': 412, 'error': 'precondition failed'})
    response.status_code = 412
    return response


def too_many_requests(message, limit=None):
    response = jsonify({'status': 429, 'error': 'too many requests',
                        'message': message})
    response.status_code = 429
    return response
