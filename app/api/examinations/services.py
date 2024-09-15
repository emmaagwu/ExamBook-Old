from .models import ExamQuestion, Exam, ExamSubmission, SubmissionAnswer
from ..questions.models import Question
from ..utils.db import db

def get_all_exams():
    return Exam.query.all()

def get_exam_by_id(exam_id):
    return Exam.query.get(exam_id)

def create_exam(data):
    exam = Exam(
        title=data['title'],
        description=data.get('description'),
        total_marks=data['total_marks'],
        duration=data['duration'],
        user_id=data['user_id']
    )
    db.session.add(exam)
    db.session.commit()
    return exam

def update_exam(exam_id, data, user_id):
    exam = Exam.query.get(exam_id)
    if not exam:
        return None
    
    # Ensure that only the creator of the exam can update it
    if exam.user_id != user_id:
        raise PermissionError("You do not have permission to update this exam.")
    
    exam.title = data['title']
    exam.description = data.get('description')
    exam.total_marks = data['total_marks']
    exam.duration = data['duration']
    db.session.commit()
    return exam

def delete_exam(exam_id, user_id):
    exam = Exam.query.get(exam_id)
    if not exam:
        return None
    
    # Ensure that only the creator of the exam can delete it
    if exam.user_id != user_id:
        raise PermissionError("You do not have permission to delete this exam.")
    
    db.session.delete(exam)
    db.session.commit()
    return exam




def get_exam_questions(exam_id):
    exam = Exam.query.get(exam_id)
    if not exam:
        raise ValueError(f"Exam with ID {exam_id} not found")
    
    return ExamQuestion.query.filter_by(exam_id=exam_id).all()

def add_question_to_exam(exam_id, data):
    exam = Exam.query.get(exam_id)
    if not exam:
        raise ValueError(f"Exam with ID {exam_id} not found")

    question_id = data.get('question_id')
    question = Question.query.get(question_id)
    if not question:
        raise ValueError(f"Question with ID {question_id} not found")

    marks = data.get('marks', 0)
    if marks <= 0:
        raise ValueError("Marks must be greater than 0")
    
    exam_question = ExamQuestion(
        exam_id=exam_id,
        question_id=question_id,
        marks=marks
    )

    db.session.add(exam_question)
    db.session.commit()
    return exam_question

def remove_question_from_exam(exam_id, question_id):
    exam_question = ExamQuestion.query.filter_by(exam_id=exam_id, question_id=question_id).first()
    if not exam_question:
        raise ValueError(f"Question with ID {question_id} not found in exam with ID {exam_id}")
    
    db.session.delete(exam_question)
    db.session.commit()



# Service to create an exam submission
def create_submission(exam_id, user_id, answers):
    submission = ExamSubmission(exam_id=exam_id, user_id=user_id)
    db.session.add(submission)
    db.session.commit()

    # Saving each answer for the submission
    for answer in answers:
        submission_answer = SubmissionAnswer(
            submission_id=submission.id,
            question_id=answer['question_id'],
            answer=answer['answer']
        )
        db.session.add(submission_answer)

    db.session.commit()
    return submission

# Service to get all submissions for an exam
def get_all_submissions(exam_id):
    return ExamSubmission.query.filter_by(exam_id=exam_id).all()

# Service to get a single submission
def get_submission_by_id(exam_id, submission_id):
    return ExamSubmission.query.filter_by(id=submission_id, exam_id=exam_id).first()

# Service to grade a submission
def grade_submission(submission_id, score):
    submission = ExamSubmission.query.get(submission_id)
    if submission and not submission.graded:
        submission.score = score
        submission.graded = True
        db.session.commit()
    return submission

# Service to get all answers for a submission
def get_submission_answers(submission_id):
    return SubmissionAnswer.query.filter_by(submission_id=submission_id).all()

# Service to update a specific answer in a submission (optional)
def update_submission_answer(submission_id, answer_id, new_answer):
    submission_answer = SubmissionAnswer.query.filter_by(id=answer_id, submission_id=submission_id).first()
    if submission_answer:
        submission_answer.answer = new_answer['answer']
        db.session.commit()
    return submission_answer