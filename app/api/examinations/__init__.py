from flask_restx import Namespace
from .controller import register_routes

examination_ns = Namespace('exams', description='Operations related to exams and submissions')

register_routes(examination_ns)
