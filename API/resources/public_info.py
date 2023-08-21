from datetime import datetime

from flask_restful import Resource, reqparse, marshal_with, fields, marshal, abort

from API.common.helper import is_valid_params, convert_info
from API.common.model import db, User, PublicInfo

public_info_fields = {
    'id': fields.Integer,
    'likes': fields.Integer,
    'total_price': fields.Integer,
    'author': fields.String,
    'title': fields.String,
    # 'date': fields.DateTime,
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
args_parser.add_argument('user_id', type=int, required=False, location='args')
args_parser.add_argument('limit', type=int, required=False, location='args')
args_parser.add_argument('date', type=lambda x: datetime.strptime(x, '%Y-%m-%d'), required=False,
                         location='args')
args_parser.add_argument('title', type=str, required=False, location='args')
args_parser.add_argument('params', type=str, required=False, location='args')

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
        
        if args['user_id']:
            user = db.one_or_404(db.select(User).filter_by(id=args['user_id']))
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
            if args['user_id']:
                query = query.filter(PublicInfo.user_id == args['user_id'])
            if args['limit']:
                query = query.limit(args['limit'])
            if args['date']:
                query = query.filter(PublicInfo.date >= args['date'])

            results = query.all()
        results = convert_info(results, params)

        return results

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
