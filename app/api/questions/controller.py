from flask_restx import Resource, fields
from .services import get_all_questions, get_question_by_id, create_question, update_question, delete_question
from flask_jwt_extended import jwt_required,get_jwt_identity
from ..models.users import User

def register_routes(api):
    question_model = api.model('Question', {
        'id': fields.Integer(readOnly=True, description='The unique identifier of a question'),
        'subject_id': fields.Integer(required=True, description='The subject of the question'),
        'question_text': fields.String(required=True, description='The text of the question'),
        'question_type': fields.String(
            required=True,
            description='The type of the question (e.g., multiple_choice, true_false)',
            enum=['short_answer', 'multiple_choice', 'true_false']
        ),
        'options': fields.List(fields.String, description='The possible options for a multiple-choice question'),
        'correct_answer': fields.String(required=True, description='The correct answer to the question'),
        'created_at': fields.DateTime(readOnly=True),
        'updated_at': fields.DateTime(readOnly=True),
    })

    @api.route('/')
    class QuestionList(Resource):
        @api.marshal_list_with(question_model)
        @jwt_required() 
        def get(self):
            """List all questions"""
            return get_all_questions()
        
        @api.expect(question_model)
        @api.marshal_with(question_model, code=201)
        @jwt_required()
        def post(self):
            """Create a new question"""
            current_user_id = get_jwt_identity()
            payload = api.payload
            payload['user_id'] = current_user_id            
            return create_question(payload), 201


    @api.route('/<int:id>')
    @api.response(404, 'Question not found')
    @api.param('id', 'The question identifier')
    class Question(Resource):
        @jwt_required()
        @api.marshal_with(question_model)
        def get(self, id):
            """Fetch a question by its ID"""
            question = get_question_by_id(id)
            if not question:
                api.abort(404, f"Question {id} not found")
            return question

        @jwt_required()
        @api.expect(question_model)
        @api.marshal_with(question_model)
        def put(self, id):
            """Update a question given its ID"""
            current_user_id = get_jwt_identity()
            question = update_question(id, api.payload, current_user_id)
            if not question:
                api.abort(404, f"Question {id} not found")
            return question

        @jwt_required()
        @api.response(204, 'Question deleted')
        def delete(self, id):
            """Delete a question given its ID"""
            current_user_id = get_jwt_identity()
            question = delete_question(id, current_user_id)
            if not question:
                api.abort(404, f"Question {id} not found")
            return '', 204
