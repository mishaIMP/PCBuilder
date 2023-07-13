from flask_restful import Resource, reqparse, marshal_with, fields, marshal, abort
from flask import Blueprint

from API.common.helper import convert_data, COMPONENTS
from API.common.model import db, User, Components, Prices, Amounts, Links, Additional, PublicInfo

comp_blueprint = Blueprint('components', __name__)

put_parser = reqparse.RequestParser()
put_parser.add_argument('comp', type=str, required=False)
put_parser.add_argument('model', type=str, required=False)
put_parser.add_argument('price', type=str, required=False)
put_parser.add_argument('amount', type=str, required=False)
put_parser.add_argument('link', type=str)

post_parser = reqparse.RequestParser()
post_parser.add_argument('info_id', type=int, required=True, help='info_id is required')

args_parser = reqparse.RequestParser()
args_parser.add_argument('comps', type=str, required=False, location='args')


additional_fields = {
    'comp': fields.String,
    'model': fields.String,
    'price': fields.Integer,
    'amount': fields.Integer,
    'link': fields.String
}


class ComponentsResource(Resource):
    def get(self, comp_id=None):
        if comp_id:
            comp = db.one_or_404(db.select(Components).filter_by(id=comp_id))
            price = comp.prices[0]
            amount = comp.amounts[0]
            link = comp.links[0]
            additional = comp.additional
            args = args_parser.parse_args()
            params = args.get('comps', None)
            if params:
                result = {}
                for param in params.split('-'):
                    if param in COMPONENTS:
                        result[param] = convert_data(comp, price, amount, link, additional, specific=param)
                    else:
                        additional = db.first_or_404(db.select(Additional).filter_by(comp=param))
                        if 'additional' not in result:
                            result['additional'] = []
                        result['additional'].append(marshal(additional, additional_fields))
            else:
                result = convert_data(comp, price, amount, link, additional)
            return result, 200

        return abort(404)

    def post(self):
        """init pc"""
        args = post_parser.parse_args()
        public_info = db.one_or_404(db.select(PublicInfo).filter_by(id=args['info_id']))
        components = Components(public_info_id=public_info.id)
        db.session.add(components)
        db.session.commit()
        prices = Prices(comp_id=components.id)
        db.session.add(prices)
        amounts = Amounts(comp_id=components.id)
        db.session.add(amounts)
        links = Links(comp_id=components.id)
        db.session.add(links)
        db.session.commit()
        return {'comp_id': components.id}, 201

    def put(self):
        # args = put_parser.parse_args()
        # if args['comp'] in COMPONENTS:
        #     comp = db.one_or_404(db.select(Components).filter_by(id=args['info_id']))
        #     comp.__setattr__(args['comp'], args['model'])
        #     price = comp.prices[0]
        #     price.__setattr__(args['comp'], args['price'])
        #     amount = comp.amounts[0]
        #     amount.__setattr__(args['comp'], args['amount'])
        #     link = comp.links[0]
        #     link.__setattr__(args['comp'], args['link'])
        # else:
        #     additional = Additional(**args)
        #     db.session.add(additional)
        #
        # db.session.commit()
        return {'status': 'ok'}, 201

    def patch(self, comp_id=None):
        if not comp_id:
            abort(404)
        args = put_parser.parse_args()
        if args['comp'] in COMPONENTS:
            comp = db.one_or_404(db.select(Components).filter_by(id=comp_id))
            comp.__setattr__(args['comp'], args['model'])
            if args['price']:
                price = comp.prices[0]
                price.__setattr__(args['comp'], args['price'])
            if args['amount']:
                amount = comp.amounts[0]
                amount.__setattr__(args['comp'], args['amount'])
            else:
                amount = comp.amounts[0]
                amount.__setattr__(args['comp'], 1)
            if args['link']:
                link = comp.links[0]
                link.__setattr__(args['comp'], args['link'])
        else:
            additional = Additional(**args, comp_id=comp_id)
            db.session.add(additional)

        db.session.commit()
        return {}, 204

    def delete(self, comp_id=None):
        if not comp_id:
            abort(404)
        params = args_parser.parse_args().get('comps', None)
        if params:
            for component in params.split('-'):
                if component in COMPONENTS:
                    comp = db.one_or_404(db.select(Components).filter_by(id=comp_id))
                    price = comp.prices[0]
                    amount = comp.amounts[0]
                    link = comp.links[0]
                    for item in [comp, price, amount, link]:
                        item.__setattr__(component, None)

                else:
                    additional = db.one_or_404(db.select(Additional).filter_by(comp=component))
                    db.session.delete(additional)

        else:
            comp = db.one_or_404(db.select(Components).filter_by(id=comp_id))
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
        return {'status': 'ok'}, 202
