from flask import Flask
from flask_restx import Api
from .controllers.auth_controller import auth_namespace as auth_ns
from .utils.db import db
from .models.users import User
from .config.config import config_dict
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from .questions import questions_ns
from .subjects import subject_ns
from .examinations import examination_ns

def create_app(config=config_dict['dev']):

    app = Flask(__name__)

    app.config.from_object(config)

    db.init_app(app)

    jwt=JWTManager(app)

    migrate=Migrate(app, db)


    api=Api(app,
        title='ExamBook API',
        version='1.0',
        description='A RESTAPI for the online Examination app',
        authorizations='authorizations',
        security='Bearer Auth'
    )

    api.add_namespace(auth_ns)
    api.add_namespace(questions_ns)
    api.add_namespace(subject_ns)
    api.add_namespace(examination_ns)

    return app
