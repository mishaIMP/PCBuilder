from flask_restful import Resource, reqparse, fields, marshal_with, marshal
from API.common.model import db, User
from flask import Blueprint, request


users_blueprint = Blueprint('users', __name__)

user_fields = {
    'id': fields.Integer
}

user_list_fields = {
    'count': fields.Integer,
    'users': fields.List(fields.Nested(user_fields)),
}

post_parser = reqparse.RequestParser()
post_parser.add_argument('username', type=str,
                         help='username is required', required=True)


class UsersResource(Resource):
    def get(self, user_id=None):
        """get user by id or get list of all users"""
        if user_id:
            user = db.one_or_404(db.select(User).filter_by(id=user_id))
            print(user.id)
            return marshal(user, user_fields)
        else:
            args = request.args.to_dict()
            users = db.session.execute(
                db.select(User).order_by(User.id)).fetchall()
            # limit = args.get('limit', 0)
            # if limit:
            #     users = users.limit(limit)
            # users = users.all()

            return marshal({
                'count': len(users),
                'users': [marshal(u, user_fields) for u in users]
            }, user_list_fields), 200

    @marshal_with(user_fields)
    def post(self):
        """adding user"""
        args = post_parser.parse_args()
        user = User(**args)
        db.session.add(user)
        db.session.commit()
        return user, 201

    @marshal_with(user_fields)
    def put(self, user_id):
        args = post_parser.parse_args()
        user = db.one_or_404(db.select(User).filter_by(id=user_id))
        user.username = args['username']
        db.session.commit()
        return user, 200

    def delete(self, user_id):
        user = db.one_or_404(db.select(User).filter_by(id=user_id))
        db.session.delete(user)
        db.session.commit()
        return {'user': 'deleted'}, 202
