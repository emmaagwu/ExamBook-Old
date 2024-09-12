from ..utils.db import db
from datetime import datetime

class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationship with User model
    creator = db.relationship('User', backref='subjects', lazy=True)

    # Relationship with Question model
    questions = db.relationship('Question', backref='subject', lazy=True)

    def __repr__(self):
        return f'<Subject {self.name}>'
