from datetime import date
import re

import pytz
from flask import current_app, url_for
from jinja2 import evalcontextfilter, Markup, escape

from app import app
from app.models.card import DiceFlags


@app.template_filter('paged_title')
def paged_title(value, page=None):
    if not page or page == 1:
        return value
    return '[p. {}] {}'.format(page, value)


@app.template_filter('copyright')
def copyright_date(value):
    return '{}-{}'.format(value, date.today().year)


@app.template_filter('format_date')
def format_date(value, format='%b %d, %Y %Z'):
    result = value
    # Convert date to UTC if it lacks a timezone
    if not result.tzinfo:
        result = pytz.utc.localize(value, is_dst=None)
    return result.astimezone(pytz.timezone(current_app.config.get('LOCAL_TZ'))).strftime(format)


@app.template_filter('die_name')
def die_name(flag):
    return DiceFlags(flag).name


@app.template_filter('deck_title')
def deck_title(deck):
    return deck.title if deck.title else 'Untitled {}'.format(deck.phoenixborn.name)


@app.template_filter('first_name')
def first_name(name):
    return name.split()[0]


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


@app.template_filter('card_img')
def card_img(card, extension='jpg'):
    if extension not in ('jpg', 'png'):
        return ''
    return cdn_url('/images/cards/{}.{}'.format(card.stub, extension))


def parse_card_codes(text):
    def parse_match(match):
        if match.group(3):
            return Markup(' <span class="divider"></span> ')
        primary = match.group(1)
        lower_primary = primary.lower().replace('&#39;', '')
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
                ['<i>', lower_primary, ' ', secondary, '</i>']
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
    # Parse card codes
    text = re.sub(r'\[\[((?:[a-z -]|&#39;)+)(?::([a-z]+))?\]\]|( - )', parse_match, text, flags=re.I)
    # Parse star formatting
    # * list item
    def list_element(match):
        return Markup(''.join([match.group(1), '<li>', match.group(2), '</li>']))
    text = re.sub(r'(^|\n)\* +(.+)', list_element, text)
    def list_wrapper(match):
        return Markup(''.join([match.group(1), '<ul>', match.group(2), '</ul>\n']))
    text = re.sub(r'(^|\n)((?:<li>.+?</li>(?:\n|$))+)', list_wrapper, text)
    text = re.sub(r'(</li>)\n(<li>|</ul>)', r'\1\2', text)
    # lone star: *
    def lone_star(match):
        return Markup(''.join([match.group(1), '&#42;', match.group(2)]))
    text = re.sub(r'(^| )\*( |$)', lone_star, text, flags=re.M)
    # ***emstrong*** or ***em*strong**
    def em_strong(match):
        return Markup(''.join([
            '<b><i>', match.group(1), '</i>', match.group(2), '</b>'
        ]))
    text = re.sub(r'\*{3}(.+?)\*(.*?)\*{2}', em_strong, text)
    # ***strong**em*
    def strong_em(match):
        return Markup(''.join([
            '<i><b>', match.group(1), '</b>', match.group(2), '</i>'
        ]))
    text = re.sub(r'\*{3}(.+?)\*{2}(.*?)\*', strong_em, text)
    # **strong**
    def strong(match):
        return Markup(''.join([
            '<b>', match.group(1), '</b>'
        ]))
    text = re.sub(r'\*{2}(.+?)\*{2}', strong, text)
    # *emphasis*
    def em(match):
        return Markup(''.join([
            '<i>', match.group(1), '</i>'
        ]))
    text = re.sub(r'\*([^\*\n\r]+)\*', em, text)
    return text


_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

@app.template_filter('parse_text')
@evalcontextfilter
def parse_text(eval_ctx, text, format_paragraphs=True):
    if not text:
        return ''
    result = parse_card_codes(escape(text))
    if not format_paragraphs:
        if eval_ctx.autoescape:
            result = Markup(result)
        return result
    result = '\n\n'.join(
        '<p>{}</p>'.format(p.replace('\n', Markup('<br>\n')))
        for p in _paragraph_re.split(result.strip())
    )
    # Correct wrapped lists
    result = re.sub(r'<p><ul>', r'<ul>', result)
    result = re.sub(r'</ul></p>', r'</ul>', result)
    if eval_ctx.autoescape:
        result = Markup(result)
    return result
