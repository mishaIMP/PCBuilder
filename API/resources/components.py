from flask_restful import Resource, reqparse, marshal_with, fields, marshal, abort
from flask import Blueprint, request

from API.common.helper import COMPONENTS, is_valid_request_data
from API.common.model import AdditionalComponents, db, Components,  PublicInfo

comp_blueprint = Blueprint('components', __name__)

component_parser = reqparse.RequestParser()
component_parser.add_argument('component', type=str, required=True)
component_parser.add_argument('model', type=str, required=False)
component_parser.add_argument('price', type=str, required=False)
component_parser.add_argument('amount', type=str, required=False)
component_parser.add_argument('link', type=str)

post_args_parser = reqparse.RequestParser()
post_args_parser.add_argument('all_comp', type=bool, required=False, location='args')

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
    def get(self, info_id=None):
        if info_id:
            info = db.one_or_404(db.select(PublicInfo).filter_by(id=info_id))
            params = args_parser.parse_args()['comps']
            components = info.components
            additional = info.additional_components
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

    def post(self, info_id=None):
        if not info_id:
            abort(404)
        all_comps = post_args_parser.parse_args()['all_comps']
        public_info = db.one_or_404(db.select(PublicInfo).filter_by(id=args['info_id']))
        if all_comps:
            data = request.form.get('data', None)
            if not is_valid_request_data(data):
                abort(403)
            for pc in data:
                if pc['component'] in COMPONENTS:
                    component = Components(public_info_id=info_id, **pc)
                else:
                    component = AdditionalComponents(public_info_id=info_id, **pc)
                db.session.add(component)           
            
        else:
            args = component_parser.parse_args()
            if args['component'] in COMPONENTS:
                component = Components(public_info_id=info_id, **args)
            else:
                component = AdditionalComponents(public_info_id=info_id, **args)
            db.session.add(component)
        db.session.commit()
        return {'status': 'created'}, 201
    
    def put(self, info_id=None):
        info = db.one_or_404(db.select(PublicInfo).filter_by(id=info_id))
        data = request.form.get('data', None)
        if not is_valid_request_data(data=data):
            abort(403)
        components = info.components
        additional = info.additional_components
        for pc in data:
            if pc['component'] in COMPONENTS:
                component = list(filter(lambda c: c.component == pc['component'], components))
            else:
                component = list(filter(lambda c: c.component == pc['component'], additional))
                    
            if component:
                for item in pc:
                    component[0].__setattr__(item, pc[item])
            else:
                abort(404)
                
        db.session.commit()
        return {}, 204

    @marshal_with(component_fields)
    def patch(self, info_id=None):
        if not info_id:
            abort(404)
        args = component_parser.parse_args()
        info = db.one_or_404(db.select(PublicInfo).filter_by(id=info_id))
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

    def delete(self, info_id=None):
        if not info_id:
            abort(404)
        info = db.one_or_404(db.select(PublicInfo).filter_by(id=info_id))
        components = info.components
        additional = info.additional_components
        params = args_parser.parse_args().get('comps')
        if not params:
            params = COMPONENTS
        else:
            params = params.split('-')
        if components:
            for comp in components:
                if comp.component in params:
                    db.session.delete(comp)
        
        if additional:
            for comp in additional:
                if comp.component in params:
                    db.session.delete(comp)
        db.session.commit()
        return {'status': 'deleted'}, 202
