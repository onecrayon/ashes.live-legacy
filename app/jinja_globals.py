from datetime import date
import re
from urllib.parse import unquote

import pytz
from flask import current_app, url_for
from jinja2 import evalcontextfilter, Markup, escape

from app import app
from app.models.card import DiceFlags
from app.utils.stream import next_subscription_link


@app.context_processor
def global_values():
    """Declare global variables and methods for use in Jinja templates"""
    return {
        'next_subscription_link': next_subscription_link
    }


@app.template_filter('paged_title')
def paged_title(value, page=None):
    if not page or page == 1:
        return value
    return '{} [p. {}]'.format(value, page)


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
    is_dict = isinstance(deck, dict)
    title = deck.title if not is_dict else deck.get('title')
    phoenixborn = deck.phoenixborn.name if not is_dict else deck['phoenixborn']['name']
    return title if title else 'Untitled {}'.format(phoenixborn)


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
    return '{}{}'.format(
        current_app.config['CDN_URL'] if current_app.config['CDN_URL']
        else current_app.config['SITE_URL'],
        url
    )


@app.template_filter('badge_link')
def badge_link(url):
    def parse_badge(match):
        return unquote(match.group(0))
    return re.sub(r'/[0-9](?:[a-z0-9-]|%2[ab16]|%3d)+(?:[a-z0-9]|%2[a1])(?:/|$)', parse_badge, url, count=1, flags=re.I)


@app.template_filter('card_img')
def card_img(card, extension='jpg'):
    if extension not in ('jpg', 'png'):
        return ''
    return cdn_url('/images/cards/{}.{}'.format(card.stub, extension))


def parse_card_codes(text):
    # Normalize linebreaks to Unix; for some reason I was getting CRLF from the database
    text = re.sub(r'\r\n|\r', r'\n', text)
    # Parse arbitrary links; e.g. [[My deck ashes.live/decks/123]] or https://ashes.live/decks/123
    def parse_url(match):
        text_url = match.group(2) if match.group(2) else match.group(3)
        internal_link = re.match(r'(https?://)?ashes\.live', text_url, flags=re.I) is not None
        def parse_url_prefix(match):
            if internal_link:
                return 'https://' + match.group(2)
            elif not match.group(1):
                return 'http://' + match.group(2)
            else:
                return match.group(0)
        parsed_url = re.sub(r'^(https?://)?(.+)$', parse_url_prefix, text_url)
        text = match.group(1).strip() if match.group(1) else None
        return ''.join([
             '<a href="', parsed_url, '"', ' rel="nofollow"' if not internal_link else '', '>',
            text if text else text_url, '</a>'
        ])
    text = re.sub(
        r'\[\[([^\]]*?)((?:https?://|\b)[^\s/$.?#]+\.[^\s*]+?)\]\]|(https?://[^\s/$.?#]+\.[^\s*]+?(?=[.?!]|\s|$))',
        parse_url, text, flags=re.I
    )
    # Parse player links; e.g. [[Username#1234]] or [[#1234]]
    def parse_badges(match):
        """
        const text = text ? text.trim() : null
		return [
			'<a class="username" href="', globals.playerUrl(badge), '">',
			text ? text : '', '<span class="badge">', badge, '</span></a>'
		].join('')
        """
        text = match.group(1).strip() if match.group(1) else None
        badge = match.group(2)
        return ''.join([
            '<a class="username" href="', badge_link(url_for('player.view', badge=badge)), '">',
			text if text else '', '<span class="badge">', badge, '</span></a>'
        ])
    text = re.sub(r'\[\[([^\]]*?)#([0-9][a-z0-9*&+=-]+[a-z0-9*!])\]\]', parse_badges, text, flags=re.I)
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
    # Parse blockquotes
    def parse_blockquotes(match):
        return Markup(''.join([
            '<blockquote>',
            re.sub(r'^>[ \t]*', r'', match.group(0), flags=re.M),
            '</blockquote>'
        ]))
    text = re.sub(r'^&gt;', '>', text, flags=re.M)
    text = re.sub(r'(^> ?.+?)(?=(\n[^>\n])|\Z)', parse_blockquotes, text, flags=re.M|re.S)
    text = text.replace('\n</blockquote>', '</blockquote>\n')
    # Parse star formatting
    # * list item
    def list_element(match):
        return Markup(''.join([match.group(1), '<li>', match.group(2), '</li>']))
    text = re.sub(r'(^|\n|<blockquote>)\* +(.+)', list_element, text)
    text = text.replace('</blockquote></li>', '</li></blockquote>')
    def list_wrapper(match):
        return Markup(''.join([match.group(1), '<ul>', match.group(2), '</ul>', match.group(3)]))
    text = re.sub(r'(^|\n|<blockquote>)((?:<li>.+?</li>\n?)+)(</blockquote>|\n|$)', list_wrapper, text)
    text = text.replace('</li>\n<li>', '</li><li>')
    text = text.replace('</li>\n</ul>', '</li></ul>\n')
    # Fix single linebreaks after a block level elements (these break the paragraph logic)
    def fix_spacing(match):
        return Markup(match.group(1) + '\n')
    text = re.sub(r'(</(?:blockquote|ul)>\n)(?=[^\n])', fix_spacing, text)
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
    # Correct wrapped lists and blockquotes
    result = re.sub(r'<p>((?:<blockquote>)?<ul>)', r'\1', result)
    result = re.sub(r'(</ul>(?:</blockquote>)?)</p>', r'\1', result)
    result = result.replace('<p><blockquote>', '<blockquote><p>')
    result = result.replace('</blockquote></p>', '</p></blockquote>')
    if eval_ctx.autoescape:
        result = Markup(result)
    return result
