from flask_restful import Resource, reqparse, fields, marshal_with, marshal
from API.common.model import db, User
from flask import Blueprint, request


users_blueprint = Blueprint('users', __name__)

user_fields = {
    'id': fields.Integer,
    'username': fields.String
}

user_list_fields = {
    'count': fields.Integer,
    'users': fields.List(fields.Nested(user_fields))
}

post_parser = reqparse.RequestParser()
post_parser.add_argument('username', type=str, help='username is required', required=True)

get_parser = reqparse.RequestParser()
get_parser.add_argument('username', type=str, required=False, location='args')


class UsersResource(Resource):
    def get(self, user_id=None):
        username = get_parser.parse_args()['username']
        if username:
            user = db.one_or_404(db.select(User).filter_by(username=username))
            return marshal(user, user_fields)
        if user_id:
            user = db.one_or_404(db.select(User).filter_by(id=user_id))
            return marshal(user, user_fields)

        users = db.session.execute(db.select(User).order_by(User.id)).scalars().all()
        return marshal({
            'count': len(users),
            'users': [marshal(u, user_fields) for u in users]
        }, user_list_fields), 200

    @marshal_with(user_fields)
    def post(self):
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
        public_info = user.public_info
        if public_info:
            for info in public_info:
                components = info.components
                if components:
                    comp = components[0]
                    price = comp.prices
                    amount = comp.amounts
                    link = comp.links
                    additional = comp.additional
                    for table in [price, amount, link, additional]:
                        if table:
                            for row in table:
                                db.session.delete(row)
                    db.session.commit()
                    db.session.delete(comp)
                    db.session.commit()
            db.session.delete(public_info)
            db.session.commit()
        db.session.delete(user)
        db.session.commit()

        return {'status': 'ok'}, 202
