from flask import request
from ..models import db, Student
from ..decorators import json, paginate, etag
from . import api


@api.route('/students/', methods=['GET'])
@etag
@paginate()
def get_students():
    return Student.query


@api.route('/students/<int:id>', methods=['GET'])
@etag
@json
def get_student(id):
    return Student.query.get_or_404(id)


@api.route('/students/<int:id>/registrations/', methods=['GET'])
@etag
@paginate()
def get_student_registrations(id):
    student = Student.query.get_or_404(id)
    return student.registrations


@api.route('/students/', methods=['POST'])
@json
def new_student():
    student = Student().from_json(request.json)
    db.session.add(student)
    db.session.commit()
    return {}, 201, {'Location': student.get_url()}


@api.route('/students/<int:id>', methods=['PUT'])
@json
def edit_student(id):
    student = Student.query.get_or_404(id)
    student.from_json(request.json)
    db.session.add(student)
    db.session.commit()
    return {}


@api.route('/students/<int:id>', methods=['DELETE'])
@json
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return {}
