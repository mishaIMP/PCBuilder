import datetime as dt
from functools import wraps

import jwt

from flask import current_app, request
from flask_restful import abort


class AuthToken:
    def __init__(self, user, db):
        self.user_model = user
        self.db = db

    @staticmethod
    def encode_token(user):
        payload = {
            "exp": dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=1),
            "id": str(user.id)
        }
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm="HS256")
        return token

    @staticmethod
    def decode_token(token):
        return jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms="HS256",
            options={"require_exp": True}
        )

    def check_token(self, token):
        try:
            self.decode_token(token)
            return True
        except Exception as ex:
            print(ex)
            return False

    def get_user_id(self, token):
        try:
            data = self.decode_token(token)
            return data.get('id')
        except Exception as ex:
            print(ex)
            return None

    def __call__(self, f):
        @wraps(f)
        def decorator(*args, **kwargs):
            token = None

            if 'Authorization' in request.headers:
                token = request.headers.get('Authorization')

            if not token:
                return abort(403)
            user_id = self.get_user_id(token)
            if not user_id:
                return abort(403)
            user = self.db.one_or_404(self.db.select(self.user_model).filter_by(id=user_id))
            return f(user, *args, **kwargs)

        return decorator

    def load_user_id(self, f):
        @wraps(f)
        def decorator(*args, **kwargs):
            token = None

            if 'Authorization' in request.headers:
                token = request.headers.get('Authorization')
            if not token:
                return f(None, *args, **kwargs)
            user_id = self.get_user_id(token)
            return f(user_id, *args, **kwargs)
        return decorator
