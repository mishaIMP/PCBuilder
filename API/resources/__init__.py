from flask import Flask
from flask_restful import Api


def create_app(config_filename):
    app = Flask(__name__)
    api = Api(app)
    app.config.from_object(config_filename)

    from API.resources.users import UsersResource
    from API.resources.comp import ComponentsResource

    api.add_resource(UsersResource, '/users', '/users/<int:user_id>')
    api.add_resource(ComponentsResource, '/comp', '/comp/<int:comp_id>', '/add_comp/<int:user_id>')

    return app
