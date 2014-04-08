from flask import url_for, request
from ..models import db, Class
from ..decorators import json, paginate, etag
from . import api


@api.route('/classes/', methods=['GET'])
@etag
@paginate()
def get_classes():
    return Class.query


@api.route('/classes/<int:id>', methods=['GET'])
@etag
@json
def get_class(id):
    return Class.query.get_or_404(id)


@api.route('/classes/<int:id>/registrations/', methods=['GET'])
@etag
@paginate()
def get_class_registrations(id):
    class_ = Class.query.get_or_404(id)
    return class_.registrations


@api.route('/classes/', methods=['POST'])
@json
def new_class():
    class_ = Class().from_json(request.json)
    db.session.add(class_)
    db.session.commit()
    return {}, 201, {'Location': class_.get_url()}


@api.route('/classes/<int:id>', methods=['PUT'])
@json
def edit_class(id):
    class_ = Class.query.get_or_404(id)
    class_.from_json(request.json)
    db.session.add(class_)
    db.session.commit()
    return {}


@api.route('/classes/<int:id>', methods=['DELETE'])
@json
def delete_class(id):
    class_ = Class.query.get_or_404(id)
    db.session.delete(class_)
    db.session.commit()
    return {}
