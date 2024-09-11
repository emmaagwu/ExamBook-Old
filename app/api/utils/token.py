import jwt
import datetime
from flask import current_app

def generate_reset_token(user_id):
    expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    payload = {
        'exp': expiry,
        'iat': datetime.datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def verify_reset_token(token):
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
