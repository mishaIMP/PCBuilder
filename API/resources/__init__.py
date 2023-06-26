from flask import Flask
from flask_restful import Api


def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)

    from API.resources.users import UsersResource, users_blueprint
    from API.resources.comp import ComponentsResource, comp_blueprint

    # app.register_blueprint(users_blueprint)
    # app.register_blueprint(comp_blueprint)
    # user_api = Api(users_blueprint)
    # comp_api = Api(comp_blueprint)
    api = Api(app)

    api.add_resource(UsersResource, '/users', '/users/<int:user_id>')
    api.add_resource(ComponentsResource, '/comp', '/add_comp/<int:user_id>')

    return app
