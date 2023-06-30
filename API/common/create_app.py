from flask import Flask
from flask_restful import Api

from .model import db, migrate


def create_app(config_filename):
    app = Flask(__name__, instance_relative_config=True)
    api = Api(app)
    app.config.from_pyfile(config_filename)

    db.init_app(app)

    with app.app_context():
        migrate.init_app(app, db)

    from API.resources.users import UsersResource
    from API.resources.comp import ComponentsResource

    api.add_resource(UsersResource, '/users', '/users/<int:user_id>')
    api.add_resource(ComponentsResource, '/comp', '/comp/<int:comp_id>', '/add_comp/<int:user_id>')

    return app