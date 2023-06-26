from flask_restful import Resource, reqparse, marshal_with, fields
from flask import Blueprint
from API.common.model import db, User, Components, Prices, Amounts, Links, Additional

comp_blueprint = Blueprint('components', __name__)

put_parser = reqparse.RequestParser()
put_parser.add_argument('comp_id', type=int, required=True, help='comp_id is required')
put_parser.add_argument('comp', type=str, required=True, help='comp is required')
put_parser.add_argument('name', type=str, required=True, help='name is required')
put_parser.add_argument('price', type=str, required=True, help='price is required')
put_parser.add_argument('amount', type=str, required=True, help='amount is required')
put_parser.add_argument('link', type=str)


class ComponentsResource(Resource):
    def get(self, comp_id=None):
        if comp_id:
            pass
        else:
            pass

    def post(self, user_id=None):
        """init pc"""
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
        return {"comp_id": components.id}, 201

    def put(self):
        args = put_parser.parse_args()
        components = {'cpu': Components.cpu, 'gpu': Components.gpu, 'motherboard': Components.motherboard,
                      'ram': Components.ram, 'case': Components.case, 'storage': Components.storage,
                      'psu': Components.psu, 'culler': Components.culler, 'fan': Components.fan}
        if args['comp'] in components:
            comp = db.one_or_404(db.select(Components).filter_by(id=args['comp_id']))

        else:
            additional = Additional(**args)
            db.session.add(additional)
        db.session.commit()

    def delete(self):
        pass
