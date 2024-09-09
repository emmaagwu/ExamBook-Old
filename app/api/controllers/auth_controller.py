from flask_restx import Namespace,Resource,fields

auth_namespace=Namespace('auth', description='a namespace for authentication')



@auth_namespace.route('/signup')
class Signup(Resource):
    
    def post(self):
        """
            Create a new user
        """
        pass
