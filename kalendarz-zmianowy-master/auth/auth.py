import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

SECRET_KEY = 'ajjhd897932ejnd9903mndfnkjdfnkjdsuf8972318192ndo2189-00'
TOKEN_EXPIRATION_TIME_MINUTES = 1440


def generate_token(user_id):
    expiration_time = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION_TIME_MINUTES)
    payload = {'_id': user_id, 'exp': expiration_time}
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload['_id']
        return user_id
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        user_id = verify_token(token)
        if user_id is None:
            return jsonify({'message': 'Invalid token'}), 401

        return f(user_id, *args, **kwargs)

    return decorated
