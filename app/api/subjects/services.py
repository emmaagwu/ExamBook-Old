from .models import Subject
from flask_jwt_extended import get_jwt_identity
from ..utils.db import db

def get_all_subjects():
    return Subject.query.all()

def get_subject_by_id(subject_id):
    return Subject.query.get(subject_id)

def create_subject(data):
    subject = Subject(
        name=data['name'],
        description=data.get('description'),
        creator_id=data['creator_id']
    )
    db.session.add(subject)
    db.session.commit()
    return subject

def update_subject(subject_id, data):
    subject = Subject.query.get(subject_id)
    if not subject:
        return None
    if 'name' in data:
        subject.name = data['name']
    if 'description' in data:
        subject.description = data['description']
    db.session.commit()
    return subject

def delete_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        return None
    # Check if the current user is the creator of the subject
    if subject.creator_id != get_jwt_identity():
        return None
    # Delete all associated questions
    for question in subject.questions:
        db.session.delete(question)
    db.session.delete(subject)
    db.session.commit()
    return subject

    