from flask import Flask
from flask_restx import Api


def create_app():

    app = Flask(__name__)


    api=Api(app,
        title='ExamBook API',
        version='1.0',
        description='A RESTAPI for the online Examination app',
        authorizations='authorizations',
        security='Bearer Auth'
    )

    return app
