from flask_restx import Resource, fields
from .services import get_all_subjects, get_subject_by_id, create_subject, update_subject, delete_subject
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.users import User

def register_routes(api):
    subject_model = api.model('Subject', {
        'id': fields.Integer(readOnly=True, description='The unique identifier of a subject'),
        'name': fields.String(required=True, description='The name of the subject'),
        'description': fields.String(description='A description of the subject'),
        'created_at': fields.DateTime(readOnly=True),
        'updated_at': fields.DateTime(readOnly=True),
    })

    @api.route('/')
    class SubjectList(Resource):
        @api.marshal_list_with(subject_model)
        @jwt_required()
        def get(self):
            """List all subjects"""
            return get_all_subjects()

        @api.expect(subject_model)
        @api.marshal_with(subject_model, code=201)
        @jwt_required()
        def post(self):
            """Create a new subject"""
            current_user_id = get_jwt_identity()                        
            payload = api.payload
            payload['creator_id'] = current_user_id
            return create_subject(payload), 201

    @api.route('/<int:id>')
    @api.response(404, 'Subject not found')
    @api.param('id', 'The subject identifier')
    class Subject(Resource):
        @api.marshal_with(subject_model)
        @jwt_required()
        def get(self, id):
            """Fetch a subject by its ID"""
            subject = get_subject_by_id(id)
            if not subject:
                api.abort(404, f"Subject {id} not found")
            return subject

        @api.expect(subject_model)
        @api.marshal_with(subject_model)
        @jwt_required()
        def put(self, id):
            """Update a subject given its ID"""
            subject = update_subject(id, api.payload)
            if not subject:
                api.abort(404, f"Subject {id} not found")
            return subject

        @api.response(204, 'Subject deleted')
        @jwt_required()
        def delete(self, id):
            """Delete a subject given its ID"""
            subject = delete_subject(id)
            if not subject:
                api.abort(404, f"Subject {id} not found")
            return '', 204
