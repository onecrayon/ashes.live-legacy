from datetime import date

from app import app
from app.models.card import DiceFlags


@app.template_filter('copyright')
def copyright(value):
    return '{}-{}'.format(value, date.today().year)


@app.template_filter('die_name')
def die_name(flag):
    return DiceFlags(flag).name


@app.template_filter('deck_title')
def deck_title(deck):
    return deck.title if deck.title else 'Untitled ' + deck.phoenixborn.name
