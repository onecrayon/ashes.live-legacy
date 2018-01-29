from flask import Blueprint, jsonify, render_template

from app.exceptions import ApiError

mod = Blueprint('error_handlers', __name__)


@mod.app_errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@mod.app_errorhandler(ApiError)
def handle_api_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
