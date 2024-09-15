from flask_restx import Namespace,Resource,fields
from ..models.users import User, TokenBlacklist
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, current_app
from http import HTTPStatus
from werkzeug.exceptions import Conflict, BadRequest
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required,get_jwt_identity, get_jwt
from ..utils.token import generate_reset_token, verify_reset_token
from ..utils.db import db
from flask_mail import Message, Mail
from datetime import datetime, timedelta
from decouple import config


auth_namespace=Namespace('auth', description='a namespace for authentication')

SignUp_model = auth_namespace.model(
    'SignUp', {
        'username': fields.String(required=True, description='Username of the user'),
        'email': fields.String(required=True, description='Email of the user'),
        'password': fields.String(required=True, description='Password of the user'),
        'admin_code': fields.String(required=False, description='Secret code to create an admin account')  # NEW FIELD
    }
)

User_model = auth_namespace.model(
    'User', {
        'id': fields.Integer(),
        'username': fields.String(required=True, description='The username of the user'),
        'email': fields.String(required=True, description='The email of the user'),
        'password_hash': fields.String(required=True, description='The password of the user'),
        'created_at': fields.DateTime(description='The created time of the user'),
        'updated_at': fields.DateTime(description='The updated time of the user'),
        'is_admin': fields.Boolean(description='Indicates if the user is an admin')  # NEW FIELD in response
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
        Create a new user (admin or regular based on admin code)
        """
        data = request.get_json()

        # Check if user already exists
        existing_user = User.query.filter_by(email=data.get('email')).first()
        if existing_user:
            raise Conflict(f"User with email {data.get('email')} already exists")

        # Check for admin code
        admin_code = data.get('admin_code')
        is_admin = False

        if admin_code:
            # Compare with a predefined admin code (from environment variables)
            if admin_code == config('ADMIN_SECRET_CODE'):  # Set this in your .env file
                is_admin = True
            else:
                raise BadRequest("Invalid admin code")

        # Create the new user (admin or regular)
        new_user = User(
            username=data.get('username'),
            email=data.get('email'),
            password_hash=generate_password_hash(data.get('password')),
            is_admin=is_admin
        )

        new_user.save()

        return new_user, HTTPStatus.CREATED
        

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


        user = User.query.filter_by(email=email).first()

        if user is not None and check_password_hash(user.password_hash,password):
            access_token=create_access_token(identity=user.id)
            refresh_token=create_refresh_token(identity=user.id)
            response={
                'access_token':access_token,
                'refresh_token':refresh_token,
                'is_admin': user.is_admin
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
    


@auth_namespace.route('/logout')
class Logout(Resource):

    @jwt_required()
    def post(self):
        # Get the 'jti' (JWT ID) of the access token
        jti_access = get_jwt()['jti']
        current_user = get_jwt_identity()

        # Blacklist the access token by adding its jti to the database
        access_token_blacklist = TokenBlacklist(
            jti=jti_access,
            token_type='access',  
            user_id=current_user,
            blacklisted_at=datetime.utcnow()
        )
        db.session.add(access_token_blacklist)

        # Optionally handle the refresh token if it's being passed (e.g., in headers)
        refresh_token = request.headers.get('Authorization-Refresh')  # Assuming it's sent this way
        if refresh_token:
            try:
                # Decode the refresh token manually to get its 'jti'
                decoded_refresh_token = decode_token(refresh_token)
                jti_refresh = decoded_refresh_token['jti']

                # Blacklist the refresh token by adding its jti to the database
                refresh_token_blacklist = TokenBlacklist(
                    jti=jti_refresh,
                    token_type='refresh',  # Identify it as a refresh token
                    user_id=current_user,
                    blacklisted_at=datetime.utcnow()
                )
                db.session.add(refresh_token_blacklist)

            except Exception as e:
                return {"msg": "Failed to blacklist refresh token", "error": str(e)}, 400

        # Commit all changes to the database
        db.session.commit()

        return {"msg": "Successfully logged out"},  HTTPStatus.OK



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
