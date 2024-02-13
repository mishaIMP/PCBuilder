from datetime import datetime

from flask_restful import Resource, reqparse, marshal_with, fields, abort

from API.common.helper import is_valid_params, convert_info
from API.common.model import db, User, PublicInfo, auth_token

public_info_fields = {
    'id': fields.Integer,
    'likes': fields.Integer,
    'total_price': fields.Integer,
    'author': fields.String,
    'title': fields.String,
    'date': fields.String,
    'user_id': fields.Integer
}

list_fields = {
    'count': fields.Integer,
    'items': fields.List(fields.Nested(public_info_fields))
}

args_parser = reqparse.RequestParser()
args_parser.add_argument('min_price', type=int, required=False, location='args')
args_parser.add_argument('min_price', type=int, required=False, location='args')
args_parser.add_argument('max_price', type=int, required=False, location='args')
args_parser.add_argument('author', type=str, required=False, location='args')
args_parser.add_argument('user', type=bool, required=False, location='args')
args_parser.add_argument('limit', type=int, required=False, location='args')
args_parser.add_argument('date', type=lambda x: datetime.strptime(x, '%Y-%m-%d'), required=False,
                         location='args')
args_parser.add_argument('title', type=str, required=False, location='args')
args_parser.add_argument('params', type=str, required=False, location='args')

parser = reqparse.RequestParser()
parser.add_argument('total_price', type=int, required=False)
parser.add_argument('author', type=str, required=False)
parser.add_argument('title', type=str, required=False)

params_parser = reqparse.RequestParser()
params_parser.add_argument('params', type=str, required=False, location='args')


class InfoResource(Resource):
    @staticmethod
    @auth_token.load_user_id
    def get(user_id, info_id=None):
        args = args_parser.parse_args()
        params = args['params']
        if params == 'all':
            params = None
        if not is_valid_params(params):
            abort(404)

        if info_id:
            public_info = db.one_or_404(db.select(PublicInfo).filter_by(id=info_id))
            result = convert_info(public_info, params)
            return result

        if args['user']:
            if not user_id:
                abort(404)
            user = db.one_or_404(db.select(User).filter_by(id=user_id))
            results = user.public_info

        else:
            query = PublicInfo.query
            if args['min_price']:
                query = query.filter(PublicInfo.total_price >= args['min_price'])
            if args['max_price']:
                query = query.filter(PublicInfo.total_price <= args['max_price'])
            if args['author']:
                query = query.filter(PublicInfo.author == args['author'])
            if args['title']:
                for word in args['title'].split():
                    query = query.filter(PublicInfo.title.like('%' + word + '%'))
            if args['limit']:
                query = query.limit(args['limit'])
            if args['date']:
                query = query.filter(PublicInfo.date >= args['date'])

            results = query.all()
        results = convert_info(results, params)

        return results

    @staticmethod
    @marshal_with(public_info_fields)
    @auth_token
    def post(user):
        args = parser.parse_args()
        public_info = PublicInfo(user_id=user.id, **args)
        db.session.add(public_info)
        db.session.commit()
        return public_info, 201

    @staticmethod
    @marshal_with(public_info_fields)
    @auth_token
    def put(user, info_id=None):
        if not info_id:
            abort(404)
        if not user.is_admin and not user.is_owner(info_id):
            abort(403)
        args = parser.parse_args()
        public_info = db.one_or_404(db.select(PublicInfo).filter_by(id=info_id))
        for key, val in args.items():
            public_info.__setattr__(key, val)
        db.session.commit()
        return public_info, 201

    @staticmethod
    @marshal_with(public_info_fields)
    @auth_token
    def patch(user, info_id=None):
        if not info_id:
            abort(404)
        if not user.is_admin and not user.is_owner(info_id):
            abort(403)
        args = parser.parse_args()
        public_info = db.one_or_404(db.select(PublicInfo).filter_by(id=info_id))
        for key, val in args.items():
            if val:
                public_info.__setattr__(key, val)
        db.session.commit()
        return public_info, 204

    @staticmethod
    @auth_token
    def delete(user, info_id=None):
        if not info_id:
            abort(404)
        if user.is_admin or user.is_owner(info_id):
            params = params_parser.parse_args()['params']
            public_info = db.one_or_404(db.select(PublicInfo).filter_by(id=info_id))
            if params:
                if not is_valid_params(params):
                    abort(404)

                for param in params.split('-'):
                    public_info.__setattr__(param, None)

            else:
                db.session.delete(public_info)
            db.session.commit()
            return {'status': 'ok'}, 202
        abort(403)
