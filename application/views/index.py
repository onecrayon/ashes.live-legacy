"""Index/landing page for the site"""

from flask import Blueprint, render_template
from application import app

mod = Blueprint('index', __name__)


@mod.route('/')
def landing_page():
    return render_template('index.html')
