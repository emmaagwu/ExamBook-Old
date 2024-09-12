from flask_restx import Namespace,Resource,fields
from ..models.users import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, current_app, jsonify
from http import HTTPStatus
from werkzeug.exceptions import Conflict, BadRequest
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required,get_jwt_identity
from ..utils.token import generate_reset_token, verify_reset_token
from ..utils.db import db
from flask_mail import Message, Mail
from datetime import datetime, timedelta


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

login_model=auth_namespace.model(
  'Login', {
    'email': fields.String(required=True, description='The email of the user'),
    'password': fields.String(required=True, description='The password of the user'),
  }
)


password_reset_request_model = auth_namespace.model(
    'PasswordResetRequest', {
        'email': fields.String(required=True, description='The email of the user'),
    }
)

password_reset_model = auth_namespace.model(
    'PasswordReset', {
        'token': fields.String(required=True, description='The reset token'),
        'new_password': fields.String(required=True, description='The new password of the user'),
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
        

@auth_namespace.route('/login')
class Login(Resource):

    @auth_namespace.expect(login_model)
    def post(self):
        """
            Login a user
        """
        data = request.get_json()

        email=data.get('email')
        password=data.get('password')

        print (email)

        user = User.query.filter_by(email=email).first()

        if user is not None and check_password_hash(user.password_hash,password):
            access_token=create_access_token(identity=user.id)
            refresh_token=create_refresh_token(identity=user.id)
            response={
                'access_token':access_token,
                'refresh_token':refresh_token
            }

            return response, HTTPStatus.OK

        raise BadRequest("Invalid Username or password")


@auth_namespace.route('/refresh')
class Refresh(Resource):

    
    @jwt_required(refresh=True)
    def post(self):
        username=get_jwt_identity()

        access_token=create_access_token(identity=username)

        return {'access_token': access_token}, HTTPStatus.OK
    


# Password Reset Request Route
@auth_namespace.route('/password-reset/request')
class PasswordResetRequest(Resource):

    @auth_namespace.expect(password_reset_request_model)
    def post(self):
        """
        Request password reset
        """
        data = request.get_json()
        email = data.get('email')
        user = User.query.filter_by(email=email).first()

        if not user:
            return {'message': 'User does not exist'}, HTTPStatus.NOT_FOUND

        # Generate reset token
        reset_token = generate_reset_token(user.id)
        user.reset_token = reset_token
        user.reset_token_expiration = datetime.utcnow() + timedelta(hours=1)
        user.save()

        # Send reset email
        mail = Mail(current_app)
        msg = Message(
            subject='Password Reset Request',
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[user.email],
            body=f'Please use the following token to reset your password: {reset_token}'
        )
        mail.send(msg)

        return {'message': 'Password reset link sent'}, HTTPStatus.OK

# Password Reset Route
@auth_namespace.route('/password-reset/confirm')
class PasswordResetConfirm(Resource):

    @auth_namespace.expect(password_reset_model)
    def post(self):
        """
        Reset password
        """
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('new_password')

        user_id = verify_reset_token(token)
        if not user_id:
            return {'message': 'Invalid or expired token'}, HTTPStatus.BAD_REQUEST

        user = User.query.get(user_id)
        if not user:
            return {'message': 'User does not exist'}, HTTPStatus.NOT_FOUND

        # Update user password
        user.password_hash = generate_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expiration = None
        user.save()

        return {'message': 'Password updated successfully'}, HTTPStatus.OK

