from flask_restx import Namespace
from .controller import register_routes

questions_ns = Namespace('questions', description='Operations related to questions')

register_routes(questions_ns)