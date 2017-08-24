from flask import Blueprint, render_template

mod = Blueprint('error_handlers', __name__)


@mod.app_errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404
