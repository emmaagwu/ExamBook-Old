from .models import Question
from ..utils.db import db
from flask import jsonify, make_response

def get_all_questions():
    return Question.query.all()

def get_question_by_id(question_id):
    return Question.query.get(question_id)

def create_question(data):
    allowed_question_types = ['short_answer', 'multiple_choice', 'true_false']
    if data['question_type'] not in allowed_question_types:
        raise ValueError(f"Invalid question_type: {data['question_type']}. Must be one of {allowed_question_types}.")

    question = Question(
        subject_id=data['subject_id'],
        question_text=data['question_text'],
        question_type=data['question_type'],
        options=data.get('options'),
        correct_answer=data['correct_answer'],
        user_id=data.get('user_id')
    )
    db.session.add(question)
    db.session.commit()
    return question   


def update_question(question_id, data, user_id=None):
    question = Question.query.get(question_id)
    if not question:
        return None
    
    # Ensure that only the user who created the question can update it
    if question.user_id != user_id:
        raise PermissionError("You do not have permission to update this question.")
    
    question.subject_id = data['subject_id']
    question.question_text = data['question_text']
    question.question_type = data['question_type']
    question.options = data.get('options')
    question.correct_answer = data['correct_answer']
    db.session.commit()
    return question

def delete_question(question_id, user_id):
    question = Question.query.get(question_id)
    if not question:
        return None
    
    # Ensure that only the user who created the question can delete it
    if question.user_id!= user_id:
        raise PermissionError("You do not have permission to delete this question.")
    
    db.session.delete(question)
    db.session.commit()
    return question
