"""Deck-building and viewing public decks"""

from flask import Blueprint
from flask_login import login_required

mod = Blueprint('decks', __name__, url_prefix='/decks')


@mod.route('/')
@login_required
def player_decks():
    """View logged-in player's decks"""
    pass


@mod.route('/build/')
@mod.route('/build/<int:deck_id>')
@login_required
def edit_deck(deck_id=None):
    """Edit a deck"""
    pass


@mod.route('/all/')
def all_decks():
    """View list of all public decks"""
    pass


@mod.route('/<int:deck_id>')
def view_deck(deck_id):
    """View a public or own deck"""
    pass
