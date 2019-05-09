"""Project Phoenix information page"""

from flask import Blueprint, render_template

mod = Blueprint('phoenix', __name__, url_prefix='/phoenix')


@mod.route('/')
def index():
    return render_template('phoenix/index.html')
