from flask import Blueprint
from flask_restful import Resource, reqparse, fields, marshal_with, marshal, abort

from API.common.model import db, User, auth_token

users_blueprint = Blueprint('users', __name__)

user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'password': fields.String
}

user_list_fields = {
    'count': fields.Integer,
    'users': fields.List(fields.Nested(user_fields))
}

post_parser = reqparse.RequestParser()
post_parser.add_argument('username', type=str, help='username is required', required=True)
post_parser.add_argument('password', type=str, help='password is required', required=True)

password_parser = post_parser.copy()
password_parser.add_argument('new_password', type=str, help='new_password is required', required=True)


class UsersResource(Resource):
    @staticmethod
    @auth_token
    def get(user, user_id=None):
        if user.is_admin:
            if user_id:
                user = db.one_or_404(db.select(User).filter_by(id=user_id))
                return marshal(user, user_fields)

            users = db.session.execute(db.select(User).order_by(User.id)).scalars().all()
            return marshal({
                'count': len(users),
                'users': [marshal(u, user_fields) for u in users]
            }, user_list_fields), 200
        abort(403)

    @marshal_with(user_fields)
    def put(self, user_id):
        args = post_parser.parse_args()
        user = db.one_or_404(db.select(User).filter_by(id=user_id))
        user.username = args['username']
        db.session.commit()
        return user, 200

    @staticmethod
    @auth_token
    def delete(user, user_id):
        if user.is_admin:
            user_ = db.one_or_404(db.select(User).filter_by(id=user_id))
            assemblies = user_.public_info
            while assemblies:
                components = assemblies[0].components + assemblies[0].additional_components
                while components:
                    db.session.delete(components[0])
                db.session.commit()
                db.session.delete(assemblies[0])
                db.session.commit()

            db.session.delete(user_)
            db.session.commit()

        return {'status': 'ok'}, 202


class SignUp(Resource):
    @staticmethod
    def post():
        args = post_parser.parse_args()
        try:
            user = User(**args)

            db.session.add(user)
            db.session.commit()
            token = auth_token.encode_token(user)
            return {'jwt_token': token}, 201
        except Exception as ex:
            return {'message': str(ex)}, 400


class Login(Resource):
    @staticmethod
    def post():
        args = post_parser.parse_args()
        user = db.one_or_404(db.select(User).filter_by(username=args['username']))
        if user.check_password(args['password']):
            token = auth_token.encode_token(user)
            return {'jwt_token': token}, 200
        abort(403)


class ChangePassword(Resource):
    @staticmethod
    @auth_token
    def post(user):
        args = password_parser.parse_args()
        if user.change_password(args['username'], password=args['password'], new_password=args['new_password']):
            db.session.commit()
            return {'status': 'ok'}, 200
        abort(400)
