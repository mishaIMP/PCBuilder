from flask import Flask
from flask_restful import Api

from .model import db, migrate


def create_app(config_filename):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile(config_filename)

    db.init_app(app)

    with app.app_context():
        migrate.init_app(app, db)

    from ..resources.users import UsersResource, users_blueprint
    from ..resources.components import ComponentsResource, comp_blueprint
    from ..resources.public_info import InfoResource

    users_api = Api(users_blueprint)
    comp_api = Api(comp_blueprint)

    users_api.add_resource(UsersResource, '/users', '/users/<int:user_id>')
    comp_api.add_resource(ComponentsResource, '/comp', '/comp/<int:comp_id>')
    comp_api.add_resource(InfoResource, '/info', '/info/<int:info_id>')

    app.register_blueprint(users_blueprint)
    app.register_blueprint(comp_blueprint)

    return app
