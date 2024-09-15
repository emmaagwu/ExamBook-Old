from datetime import datetime
from ..utils.db import db

class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) 
    question_text = db.Column(db.String(255), nullable=False)
    question_type = db.Column(db.Enum('short_answer', 'multiple_choice', 'true_false', name='question_types'), nullable=False)  # e.g., 'multiple_choice', 'true_false'
    options = db.Column(db.JSON, nullable=True)  
    correct_answer = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


    def __repr__(self):
        return f'<Question {self.question_text}>'
    
