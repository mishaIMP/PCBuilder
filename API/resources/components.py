from flask import Blueprint
from flask_restful import Resource, reqparse, marshal_with, fields, marshal, abort

from API.common.helper import COMPONENTS
from API.common.model import AdditionalComponents, db, Components, BuildInfo, auth_token

comp_blueprint = Blueprint('components', __name__)

component_parser = reqparse.RequestParser()
component_parser.add_argument('component', type=str, required=True)
component_parser.add_argument('model', type=str, required=False)
component_parser.add_argument('price', type=str, required=False)
component_parser.add_argument('amount', type=str, required=False)
component_parser.add_argument('link', type=str)

post_args_parser = reqparse.RequestParser()
post_args_parser.add_argument('all_comps', type=bool, required=False, location='args')

args_parser = reqparse.RequestParser()
args_parser.add_argument('comps', type=str, required=False, location='args')

component_fields = {
    'component': fields.String,
    'model': fields.String,
    'price': fields.Integer,
    'amount': fields.Integer,
    'link': fields.String
}

list_fields = {
    'count': fields.Integer,
    'components': fields.Nested(component_fields)
}


class ComponentsResource(Resource):
    @staticmethod
    def get(info_id=None):
        if info_id:
            info = db.one_or_404(db.select(BuildInfo).filter_by(id=info_id))
            params = args_parser.parse_args()['comps']
            components = info.components
            additional = info.additional_components

            if not components and not additional:
                abort(404)

            if params:
                components = tuple(filter(lambda c: c.component in params.split('-'), components))
                additional = tuple(filter(lambda c: c.component in params.split('-'), additional))
            return {
                'comps': marshal({
                    'count': len(components),
                    'components': [marshal(c, component_fields) for c in components]
                }, list_fields),
                'additional': marshal({
                    'count': len(additional),
                    'components': [marshal(a, component_fields) for a in additional]
                }, list_fields),
            }, 200

        return abort(404)

    @staticmethod
    @auth_token
    def post(user, info_id=None):
        if not info_id:
            abort(404)
        if not user.is_admin and not user.is_owner(info_id):
            abort(403)
        args = component_parser.parse_args()
        if args['component'] in COMPONENTS:
            component = Components(build_info_id=info_id, **args)
        else:
            component = AdditionalComponents(build_info_id=info_id, **args)
        db.session.add(component)
        db.session.commit()
        return {'status': 'created'}, 201

    @staticmethod
    @auth_token
    @marshal_with(component_fields)
    def put(user, info_id=None):
        component = None
        if not info_id:
            abort(404)
        if not user.is_admin and not user.is_owner(info_id):
            abort(403)
        args = component_parser.parse_args()
        info = db.one_or_404(db.select(BuildInfo).filter_by(id=info_id))
        if args['component'] in COMPONENTS:
            components = info.components
        else:
            components = info.additional_components

        if components:
            for component in components:
                if component.component == args['component']:
                    for key in args:
                        component.__setattr__(key, args[key])
                    db.session.commit()
                    break
            else:
                abort(404)
        else:
            abort(404)
        return component, 201

    @staticmethod
    @auth_token
    @marshal_with(component_fields)
    def patch(user, info_id=None):
        component = None
        if not info_id:
            abort(404)
        if not user.is_admin and not user.is_owner(info_id):
            abort(403)
        args = component_parser.parse_args()
        info = db.one_or_404(db.select(BuildInfo).filter_by(id=info_id))
        if args['component'] in COMPONENTS:
            components = info.components
        else:
            components = info.additional_components

        if components:
            for component in components:
                if component.component == args['component']:
                    for key in args:
                        if args[key]:
                            component.__setattr__(key, args[key])
                    db.session.commit()
                    break
            else:
                abort(404)
        else:
            abort(404)
        return component, 201

    @staticmethod
    @auth_token
    def delete(user, info_id=None):
        if not info_id:
            abort(404)
        if not user.is_admin and not user.is_owner(info_id):
            abort(403)
        info = db.one_or_404(db.select(BuildInfo).filter_by(id=info_id))
        components = info.components
        additional = info.additional_components

        if not components and not additional:
            abort(404)

        params = args_parser.parse_args().get('comps')
        if not params:
            params = ['$all']
        else:
            params = params.split('-')
        if components:
            for comp in components:
                if comp.component in params or params[0] == '$all':
                    db.session.delete(comp)

        if additional:
            for comp in additional:
                if comp.component in params or params[0] == '$all':
                    db.session.delete(comp)
        db.session.commit()
        return {'status': 'deleted'}, 202
