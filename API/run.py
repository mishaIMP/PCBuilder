from flask import jsonify
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import default_exceptions

from resources import create_app
from API.common.model import db, migrate


app = create_app('config')

with app.app_context():
    db.init_app(app)
    migrate.init_app(app, db)
    # db.drop_all()
    # db.create_all()


@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return jsonify(error=str(e)), code


for ex in default_exceptions:
    app.register_error_handler(ex, handle_error)


if __name__ == '__main__':
    app.run(debug=True)

