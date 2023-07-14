from flask_restful import Resource, reqparse, marshal_with, fields, marshal, abort

from API.common.helper import is_valid_params
from API.common.model import db, User, Components, Prices, Amounts, Links, Additional, PublicInfo


public_info_fields = {
    'id': fields.Integer,
    'likes': fields.Integer,
    'total_price': fields.Integer,
    'author': fields.String,
    'title': fields.String,
    'date': fields.DateTime,
    'user_id': fields.Integer
}

list_fields = {
    'count': fields.Integer,
    'items': fields.List(fields.Nested(public_info_fields))
}


args_parser = reqparse.RequestParser()
args_parser.add_argument('min_price', type=int, required=True, help='min_price is required', location='args')
args_parser.add_argument('max_price', type=int, required=True, help='max_price is required', location='args')

parser = reqparse.RequestParser()
parser.add_argument('total_price', type=int, required=False)
parser.add_argument('author', type=str, required=False)
parser.add_argument('likes', type=int, required=False)
parser.add_argument('title', type=str, required=False)

post_parser = parser.copy()
post_parser.add_argument('user_id', type=int, required=True, help='comp is required')

params_parser = reqparse.RequestParser()
params_parser.add_argument('params', type=str, required=False, location='args')


class InfoResource(Resource):
    def get(self, info_id=None):
        public_info = db.one_or_404(db.select(PublicInfo).filter_by(id=info_id))
        if info_id:
            params = params_parser.parse_args()['params']
            if params:
                if not is_valid_params(params):
                    abort(404)

                res = {}
                for param in params.split('-'):
                    res[param] = public_info.__getattribute__(param)
                return res, 200

            return marshal(public_info, public_info_fields), 200

        args = args_parser.parse_args()
        min_price = args['min_price']
        max_price = args['max_price']
        public_info = db.session.execute(
            db.select(PublicInfo).fiter_by(min_price <= PublicInfo.total_price <= max_price)).scalars().all()
        return marshal({
            'count': len(public_info),
            'items': [marshal(i, public_info_fields) for i in public_info]
        }, list_fields), 200

    @marshal_with(public_info_fields)
    def post(self):
        args = post_parser.parse_args()
        public_info = PublicInfo(**args)
        db.session.add(public_info)
        db.session.commit()
        return public_info, 201

    @marshal_with(public_info_fields)
    def put(self, info_id=None):
        if not info_id:
            abort(404)
        args = parser.parse_args()
        public_info = db.one_or_404(db.select(PublicInfo).filter_by(id=info_id))
        for key, val in args.items():
            public_info.__setattr__(key, val)
        db.session.commit()
        return public_info, 201

    @marshal_with(public_info_fields)
    def patch(self, info_id=None):
        if not info_id:
            abort(404)
        args = parser.parse_args()
        public_info = db.one_or_404(db.select(PublicInfo).filter_by(id=info_id))
        for key, val in args.items():
            if val:
                public_info.__setattr__(key, val)
        db.session.commit()
        return public_info, 204

    def delete(self, info_id=None):
        if not info_id:
            abort(404)
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