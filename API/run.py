from flask import jsonify
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import default_exceptions

from API.common.create_app import create_app


app = create_app()


@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return jsonify(str(e)), code


for ex in default_exceptions:
    app.register_error_handler(ex, handle_error)

if __name__ == '__main__':
    app.run(debug=True)
