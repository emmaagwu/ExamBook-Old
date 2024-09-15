from datetime import datetime
from ..utils.db import db

class Exam(db.Model):
    __tablename__ = 'exams'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    total_marks = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Exam {self.title}>'



class ExamQuestion(db.Model):
    __tablename__ = 'exam_questions'

    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    marks = db.Column(db.Integer, nullable=False)  # Marks assigned to this question
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    exam = db.relationship('Exam', backref='exam_questions', lazy=True)
    question = db.relationship('Question', backref='exam_questions', lazy=True)

    def __repr__(self):
        return f'<ExamQuestion exam_id={self.exam_id} question_id={self.question_id}>'
    


class ExamSubmission(db.Model):
    __tablename__ = 'exam_submissions'

    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    score = db.Column(db.Float, nullable=True)
    graded = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    exam = db.relationship('Exam', backref='submissions', lazy=True)
    user = db.relationship('User', backref='exam_submissions', lazy=True)

    def __repr__(self):
        return f'<ExamSubmission {self.id} - Exam {self.exam_id}>'

class SubmissionAnswer(db.Model):
    __tablename__ = 'submission_answers'

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('exam_submissions.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    answer = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    submission = db.relationship('ExamSubmission', backref='answers', lazy=True)
    question = db.relationship('Question', backref='answers', lazy=True)

    def __repr__(self):
        return f'<SubmissionAnswer {self.id} - Submission {self.submission_id}>'