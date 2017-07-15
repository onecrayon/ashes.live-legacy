"""Index/landing page for the site"""

from flask import Blueprint, render_template
from application import app

mod = Blueprint('home', __name__)


@mod.route('/')
def index():
    return render_template('index.html')
