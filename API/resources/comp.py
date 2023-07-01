from flask_restful import Resource, reqparse, marshal_with, fields, marshal
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

additional_fields = {
    'comp': fields.String,
    'model': fields.String,
    'price': fields.Integer,
    'amount': fields.Integer,
    'link': fields.String
}


class ComponentsResource(Resource):
    def get(self, comp_id=None, component=None):
        if comp_id:
            comp = db.one_or_404(db.select(Components).filter_by(id=comp_id))
            price = comp.prices[0]
            amount = comp.amounts[0]
            link = comp.links[0]
            additional = comp.additional
            if component:
                if component in COMPONENTS:
                    result = convert_data(comp, price, amount, link, additional, specific=component)
                    return result, 200
                else:
                    additional = db.one_or_404(db.select(Additional).filter_by(comp=component))
                    return marshal(additional, additional_fields), 200

            else:
                result = convert_data(comp, price, amount, link, additional)
                return result, 200

        else:
            pass
        return {}, 200

    def post(self, user_id=None):
        """init pc"""
        if not user_id:
            return {'error': 'user_id is required'}
        user = db.one_or_404(db.select(User).filter_by(id=user_id))
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
            if 'link' in args:
                link = db.one_or_404(
                    db.select(Links).filter_by(comp_id=args['comp_id']))
                link.__setattr__(args['comp'], args['link'])
        else:
            additional = Additional(**args)
            db.session.add(additional)

        db.session.commit()
        return {'status': 'ok'}, 200

    def delete(self, comp_id=None, component=None):
        if not comp_id:
            return {'error': 'comp_id is required'}
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
