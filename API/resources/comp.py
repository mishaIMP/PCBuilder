from flask_restful import Resource, reqparse, marshal_with, fields, marshal
from flask import Blueprint
from API.common.model import db, User, Components, Prices, Amounts, Links, Additional

# comp_blueprint = Blueprint('components', __name__)

put_parser = reqparse.RequestParser()
put_parser.add_argument('comp_id', type=int,
                        required=True, help='comp_id is required')
put_parser.add_argument('comp', type=str, required=True,
                        help='comp is required')
put_parser.add_argument('name', type=str, required=True,
                        help='name is required')
put_parser.add_argument('price', type=str, required=True,
                        help='price is required')
put_parser.add_argument('amount', type=str, required=True,
                        help='amount is required')
put_parser.add_argument('link', type=str)

comp_fields = {
    'id': fields.Integer,
    'cpu': fields.String,
    'motherboard': fields.String,
    'ram': fields.String,
    'case': fields.String,
    'storage': fields.String,
    'psu': fields.String,
    'culler': fields.String,
    'fan': fields.String,
    'date': fields.DateTime,
    'title': fields.String,
    'image': fields.String
}

price_and_amount_field = {
    'id': fields.Integer,
    'cpu': fields.Integer,
    'motherboard': fields.Integer,
    'ram': fields.Integer,
    'case': fields.Integer,
    'storage': fields.Integer,
    'psu': fields.Integer,
    'culler': fields.Integer,
    'fan': fields.Integer
}

link_fields = {
    'id': fields.Integer,
    'cpu': fields.String,
    'motherboard': fields.String,
    'ram': fields.String,
    'case': fields.String,
    'storage': fields.String,
    'psu': fields.String,
    'culler': fields.String,
    'fan': fields.String
}

additional_field = {
    'id': fields.Integer,
    'comp': fields.String,
    'name': fields.String,
    'price': fields.Integer,
    'amount': fields.Integer,
    'link': fields.String
}

list_fields = {

    'count': fields.Integer,
    'component': fields.List(fields.Nested(additional_field))

}


class ComponentsResource(Resource):
    def get(self, comp_id=None):
        if comp_id:
            comp = db.one_or_404(db.select(Components).filter_by(id=comp_id))
            price = comp.prices
            amount = comp.amounts
            link = comp.links
            additional = comp.additional
            print(additional)
            return marshal(comp,
                           comp_fields), marshal(price[0],
                                                 price_and_amount_field), marshal(amount[0],
                                                                                  price_and_amount_field), marshal(
                link[0], link_fields), marshal({
                    'count': len(additional),
                    'components': [marshal(row, additional_field) for row in additional]

                }, list_fields)

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
        components = ['cpu', 'gpu', 'motherboard',
                      'ram', 'case', 'storage',
                      'psu', 'culler', 'fan']
        if args['comp'] in components:
            comp = db.one_or_404(
                db.select(Components).filter_by(id=args['comp_id']))
            comp.__setattr__(args['comp'], args['name'])
            price = db.one_or_404(
                db.select(Prices).filter_by(comp_id=args['comp_id']))
            price.__setattr__(args['comp'], args['price'])
            amount = db.one_or_404(
                db.select(Amounts).filter_by(comp_id=args['comp_id']))
            amount.__setattr__(args['comp'], args['amount'])
            if 'link' in args:
                amount = db.one_or_404(
                    db.select(Links).filter_by(comp_id=args['comp_id']))
                amount.__setattr__(args['comp'], args['link'])
        else:
            additional = Additional(**args)
            db.session.add(additional)

        db.session.commit()
        return {'status': 'ok'}, 200

    def delete(self, comp_id=None):
        if not comp_id:
            return {'error': 'comp_id is required'}

        comp = db.one_or_404(db.select(Components).filter_by(id=comp_id))
        price = comp.prices
        amount = comp.amounts
        link = comp.links
        additional = comp.additional
        for table in [price, amount, link, additional]:
            if table:
                for row in table:
                    if row:
                        db.session.delete(row)
        db.session.commit()
        db.session.delete(comp)
        db.session.commit()
        return {'status': 'ok'}, 202
