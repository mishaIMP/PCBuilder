from flask_restful import Resource, reqparse, marshal_with, fields, marshal, abort
from flask import Blueprint

from API.common.helper import convert_data, COMPONENTS
from API.common.model import db, User, Components, Prices, Amounts, Links, Additional

comp_blueprint = Blueprint('components', __name__)

put_parser = reqparse.RequestParser()
put_parser.add_argument('comp_id', type=int, required=True, help='comp_id is required')
put_parser.add_argument('comp', type=str, required=True, help='comp is required')
put_parser.add_argument('model', type=str, required=True, help='model is required')
put_parser.add_argument('price', type=str, required=True, help='price is required')
put_parser.add_argument('amount', type=str, required=True, help='amount is required')
put_parser.add_argument('link', type=str)

post_parser = reqparse.RequestParser()
post_parser.add_argument('user_id', type=int, required=True, help='user_id is required')

args_parser = reqparse.RequestParser()
args_parser.add_argument('comp', type=str, required=False, location='args')
args_parser.add_argument('anonim', type=bool, required=False, location='args')


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
            component = args.get('comp', None)
            if component:
                if component in COMPONENTS:
                    result = convert_data(comp, price, amount, link, additional, specific=component)
                    return result, 200
                else:
                    additional = db.first_or_404(db.select(Additional).filter_by(comp=component))
                    return marshal(additional, additional_fields), 200

            else:
                username = None
                if args['anonim']:
                    username = db.one_or_404(db.select(User.username).filter_by(id=comp.user_id))
                result = convert_data(comp, price, amount, link, additional, username=username)
                return result, 200

        return abort(404)

    def post(self):
        """init pc"""
        args = post_parser.parse_args()
        user = db.one_or_404(db.select(User).filter_by(id=args['user_id']))
        components = Components(user_id=user.id)
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
        args = put_parser.parse_args()
        if args['comp'] in COMPONENTS:
            comp = db.one_or_404(db.select(Components).filter_by(id=args['comp_id']))
            comp.__setattr__(args['comp'], args['model'])
            price = comp.prices[0]
            price.__setattr__(args['comp'], args['price'])
            amount = comp.amounts[0]
            amount.__setattr__(args['comp'], args['amount'])
            if args['link']:
                link = comp.links[0]
                link.__setattr__(args['comp'], args['link'])
        else:
            additional = Additional(**args)
            db.session.add(additional)

        db.session.commit()
        return {'status': 'ok'}, 200

    def delete(self, comp_id=None):
        if not comp_id:
            abort(404)
        component = args_parser.parse_args().get('comp', None)
        if component:
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
