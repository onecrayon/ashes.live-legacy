from datetime import date

from flask import current_app

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
    return deck.title if deck.title else 'Untitled {}'.format(deck.phoenixborn.name)


@app.template_filter('production_url')
def production_url(url):
    if current_app.config['ENVIRONMENT'] == 'development':
        return url
    if url.endswith('.js'):
        return url.replace('.js', '.min.js?v={}'.format(
            current_app.config['VERSION'])
        )
    if url.endswith('.css'):
        return url.replace('.css', '.min.css?v={}'.format(
            current_app.config['VERSION'])
        )
    return url
