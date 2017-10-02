"""Card gallery"""

from flask import Blueprint, render_template

mod = Blueprint('cards', __name__, url_prefix='/cards')


@mod.route('/')
def index():
    """Card gallery"""
    return render_template('wip.html')


@mod.route('/<stub>/')
def detail(stub):
    """Card details"""
    return render_template('wip.html')
