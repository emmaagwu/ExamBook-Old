from flask_restx import Namespace
from .controller import register_routes

subject_ns = Namespace('subjects', description='Operations related to subjects')

register_routes(subject_ns)
