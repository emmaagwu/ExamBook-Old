from flask_restx import Namespace,Resource,fields
from ..models.users import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request
from http import HTTPStatus
from werkzeug.exceptions import Conflict,BadRequest


auth_namespace=Namespace('auth', description='a namespace for authentication')

SignUp_model = auth_namespace.model(
    'SignUp', {
        'username': fields.String(required=True, description='Username of the user'),
        'email': fields.String(required=True, description='Email of the user'),
        'password': fields.String(required=True, description='Password of the user'),
})

User_model = auth_namespace.model(
    'User', {
        'id':fields.Integer(),
        'username':fields.String(required=True, description='The username of the user'),
        'email': fields.String(required=True, description='The email of the user'),
        'password_hash': fields.String(required=True, description='The password of the user'),
        'created_at': fields.DateTime(description='The created time of the user'),
        'updated_at': fields.DateTime(description='The updated time of the user'),
    }
)



@auth_namespace.route('/signup')
class Signup(Resource):
    
    @auth_namespace.expect(SignUp_model)
    @auth_namespace.marshal_with(User_model)
    def post(self):
        """
            Create a new user
        """
        data = request.get_json()

        try:

            new_user=User(
                username=data.get('username'),
                email=data.get('email'),
                password_hash=generate_password_hash(data.get('password'))
            )

            new_user.save()

            return new_user, HTTPStatus.CREATED

        except Exception:
            raise Conflict(f"User with email {data.get('email')} already exists") from None
        

