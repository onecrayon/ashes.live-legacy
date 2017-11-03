from datetime import date
import re

import pytz
from flask import current_app, url_for
from jinja2 import evalcontextfilter, Markup, escape

from app import app
from app.models.card import DiceFlags


@app.template_filter('copyright')
def copyright_date(value):
    return '{}-{}'.format(value, date.today().year)


@app.template_filter('format_date')
def format_date(value, format='%b %d, %Y %Z'):
    result = value
    # Convert date to UTC if it lacks a timezone
    if not result.tzinfo:
        result = pytz.utc.localize(date, is_dst=None)
    return result.astimezone(pytz.timezone(current_app.config.get('LOCAL_TZ'))).strftime(format)


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


@app.template_filter('cdn_url')
def cdn_url(url):
    if not url.startswith('/'):
        url = '/' + url
    return '{}{}'.format(current_app.config['CDN_URL'], url)


def parse_card_codes(text):
    def parse_match(match):
        if match.group(3):
            return Markup(' <span class="divider"></span> ')
        primary = match.group(1)
        lower_primary = primary.lower().replace('\'', '')
        secondary = match.group(2).lower() if match.group(2) else None
        if lower_primary in ['discard', 'exhaust']:
            return Markup(''.join(
                ['<span class="phg-', lower_primary, '" title="', primary, '"></span>']
            ))
        if lower_primary in DiceFlags.__members__ and lower_primary != 'basic':
            if not secondary:
                secondary = 'power'
        elif lower_primary == 'basic':
            secondary = 'magic'
        elif lower_primary in ['main', 'side']:
            secondary = 'action'
        elif secondary:
            return Markup(''.join(
                ['<i>', lower_primary, (' ' + secondary if secondary else ''), '</i>']
            ))
        else:
            stub = re.sub(r' ', '-', lower_primary)
            return Markup(''.join([
                '<a href="', url_for('cards.detail', stub=stub), '" class="card" target="_blank">',
                primary, '</a>'
            ]))
        return Markup(''.join([
            '<span class="phg-', lower_primary, '-', secondary, '" title="',
            primary, (' ' + secondary if secondary else ''), '"></span>'
        ]))
    return re.sub(r'\[\[([a-z\' -]+)(?::([a-z]+))?\]\]|( - )', parse_match, text, flags=re.I)


_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

@app.template_filter('parse_text')
@evalcontextfilter
def parse_text(eval_ctx, text):
    if not text:
        return ''
    result = '\n\n'.join(
        '<p>{}</p>'.format(p.replace('\n', Markup('<br>\n')))
        for p in _paragraph_re.split(escape(text))
    )
    result = parse_card_codes(result)
    if eval_ctx.autoescape:
        result = Markup(result)
    return result
