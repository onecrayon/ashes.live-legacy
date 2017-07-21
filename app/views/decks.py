"""Deck-building and viewing public decks"""

from flask import Blueprint, render_template
from flask_login import login_required

mod = Blueprint('decks', __name__, url_prefix='/decks')


@mod.route('/')
def index():
    """View list of all public decks"""
    pass


@mod.route('/<int:deck_id>/')
def view(deck_id):
    """View a public or own deck"""
    pass


@mod.route('/mine/')
@login_required
def mine():
    """View logged-in player's decks"""
    pass


@mod.route('/build/')
@mod.route('/build/<int:deck_id>/')
@login_required
def build(deck_id=None):
    """Edit a deck"""
    return render_template('decks/build.html')
