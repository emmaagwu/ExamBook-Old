from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from .services import ( create_exam, get_all_exams, get_exam_by_id, update_exam, delete_exam,
    get_exam_questions, add_question_to_exam, remove_question_from_exam,
    get_all_submissions, get_submission_by_id, create_submission,
    get_submission_answers, grade_submission, update_submission_answer
)


def register_routes(api):
    exam_model = api.model('Exam', {
        'id': fields.Integer(readOnly=True, description='The unique identifier of an exam'),
        'title': fields.String(required=True, description='The title of the exam'),
        'description': fields.String(description='A brief description of the exam'),
        'total_marks': fields.Integer(required=True, description='Total marks for the exam'),
        'duration': fields.Integer(required=True, description='Duration of the exam in minutes'),
        'created_at': fields.DateTime(readOnly=True),
        'updated_at': fields.DateTime(readOnly=True),
    })


    exam_question_model = api.model('ExamQuestion', {
        'id': fields.Integer(readOnly=True, description='The unique identifier of an exam question'),
        'exam_id': fields.Integer(required=True, description='The exam ID'),
        'question_id': fields.Integer(required=True, description='The question ID'),
        'marks': fields.Integer(required=True, description='Marks assigned to the question'),
        'created_at': fields.DateTime(readOnly=True),
    })


    # Submission model for API representation
    submission_model = api.model('Submission', {
        'id': fields.Integer,
        'exam_id': fields.Integer,
        'user_id': fields.Integer,
        'submitted_at': fields.DateTime,
        'score': fields.Float,
        'graded': fields.Boolean
    })

    # Submission answer model
    submission_answer_model = api.model('SubmissionAnswer', {
        'id': fields.Integer,
        'submission_id': fields.Integer,
        'question_id': fields.Integer,
        'answer': fields.String,
        'is_correct': fields.Boolean
    })



    @api.route('/')
    class ExamList(Resource):
        @api.marshal_list_with(exam_model)
        @jwt_required()
        def get(self):
            """List all exams"""
            return get_all_exams()
        
        @api.expect(exam_model)
        @api.marshal_with(exam_model, code=201)
        @jwt_required()
        def post(self):
            """Create a new exam"""
            current_user_id = get_jwt_identity()
            payload = api.payload
            payload['user_id'] = current_user_id
            return create_exam(payload), 201
        

    @api.route('/<int:id>')
    @api.response(404, 'Exam not found')
    @api.param('id', 'The exam identifier')
    class Exam(Resource):
        @jwt_required()
        @api.marshal_with(exam_model)
        def get(self, id):
            """Fetch an exam by its ID"""
            exam = get_exam_by_id(id)
            if not exam:
                api.abort(404, f"Exam {id} not found")
            return exam

        @jwt_required()
        @api.expect(exam_model)
        @api.marshal_with(exam_model)
        def put(self, id):
            """Update an exam given its ID"""
            current_user_id = get_jwt_identity()
            exam = update_exam(id, api.payload, current_user_id)
            if not exam:
                api.abort(404, f"Exam {id} not found")
            return exam

        @jwt_required()
        @api.response(204, 'Exam deleted')
        def delete(self, id):
            """Delete an exam given its ID"""
            current_user_id = get_jwt_identity()
            exam = delete_exam(id, current_user_id)
            if not exam:
                api.abort(404, f"Exam {id} not found")
            return '', 204


    @api.route('/<int:exam_id>/questions')
    class ExamQuestions(Resource):
        @api.marshal_list_with(exam_question_model)
        @jwt_required()
        def get(self, exam_id):
            """Get all questions in an exam"""
            return get_exam_questions(exam_id)

        @api.expect(exam_question_model)
        @api.marshal_with(exam_question_model, code=201)
        @jwt_required()
        def post(self, exam_id):
            """Add a question to an exam"""
            data = api.payload
            return add_question_to_exam(exam_id, data)
        

    @api.route('/<int:exam_id>/questions/<int:question_id>')
    @api.param('exam_id', 'The exam identifier')
    @api.param('question_id', 'The question identifier')
    class ExamQuestion(Resource):
        @jwt_required()
        @api.response(204, 'Question removed from the exam')
        def delete(self, exam_id, question_id):
            """Remove a question from an exam"""
            remove_question_from_exam(exam_id, question_id)
            return '', 204        


    

    # Exam Submission Endpoints
    @api.route('/<int:exam_id>/submissions')
    class ExamSubmissionList(Resource):
        @api.marshal_list_with(submission_model)
        @jwt_required()
        def get(self, exam_id):
            """View all submissions for a particular exam"""
            return get_all_submissions(exam_id)

        @api.expect(api.model('SubmissionCreate', {
            'answers': fields.List(fields.Nested(api.model('Answer', {
                'question_id': fields.Integer(required=True),
                'answer': fields.String(required=True)
            })))
        }))
        @api.marshal_with(submission_model, code=201)
        @jwt_required()
        def post(self, exam_id):
            """Submit an exam"""
            current_user_id = get_jwt_identity()
            payload = api.payload
            answers = payload['answers']
            return create_submission(exam_id, current_user_id, answers), 201

    @api.route('/<int:exam_id>/submissions/<int:submission_id>')
    class ExamSubmission(Resource):
        @api.marshal_with(submission_model)
        @jwt_required()
        def get(self, exam_id, submission_id):
            """View a single submission for an exam"""
            submission = get_submission_by_id(exam_id, submission_id)
            if not submission:
                api.abort(404, f"Submission {submission_id} not found")
            return submission

        @api.expect(api.model('Grade', {
            'score': fields.Float(required=True)
        }))
        @jwt_required()
        def put(self, exam_id, submission_id):
            """Grade an exam submission"""
            score = api.payload['score']
            submission = grade_submission(submission_id, score)
            if not submission:
                api.abort(404, f"Submission {submission_id} not found or already graded")
            return submission, 200

    # Submission Answers Endpoints
    @api.route('/submissions/<int:submission_id>/answers')
    class SubmissionAnswerList(Resource):
        @api.marshal_list_with(submission_answer_model)
        @jwt_required()
        def get(self, submission_id):
            """View all answers provided in a particular submission"""
            return get_submission_answers(submission_id)

    @api.route('/submissions/<int:submission_id>/answers/<int:answer_id>')
    class SubmissionAnswerUpdate(Resource):
        @api.expect(api.model('UpdateAnswer', {
            'answer': fields.String(required=True)
        }))
        @api.marshal_with(submission_answer_model)
        @jwt_required()
        def put(self, submission_id, answer_id):
            """Update an answer in a submission"""
            updated_answer = api.payload
            answer = update_submission_answer(submission_id, answer_id, updated_answer)
            if not answer:
                api.abort(404, f"Answer {answer_id} not found for submission {submission_id}")
            return answer, 200