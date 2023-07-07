from flask_restful import Resource, reqparse, marshal_with, fields, marshal, abort
from API.common.model import db, User, Components


post_parser = reqparse.RequestParser()
post_parser.add_argument('comp_id', type=int, required=True, help='comp_id is required')
post_parser.add_argument('title', type=str, required=True, help='title is required')


class TitleResource(Resource):
    def get(self):
        pass

    def post(self):
        args = post_parser.parse_args()
        comp = db.one_or_404(db.select(Components).filter_by(id=args['comp_id']))
        comp.title = args['title']
        db.session.commit()
        return {'status': 'ok'}, 201

    def put(self):
        pass

    def delete(self):
        pass
