"""Index/landing page for the site"""

from flask import Blueprint, current_app, flash, redirect, render_template, url_for

from app import db
from app.models.deck import Deck
from app.utils.decks import get_decks_query
from app.views.forms.feedback import FeedbackForm
from app.utils import send_message

mod = Blueprint('home', __name__)


@mod.route('/')
def index():
    decks = get_decks_query(options=[
        db.joinedload('phoenixborn'),
        db.joinedload('user')
    ], most_recent_public=True).order_by(Deck.created.desc()).limit(10).all()
    return render_template('index.html', recent_decks=decks)


@mod.route('/feedback/', methods=['GET', 'POST'])
def feedback():
    """Contact form"""
    form = FeedbackForm()
    if form.validate_on_submit():
        sender = form.email.data
        send_message(current_app.config['MAIL_USERNAME'], 'Help or feedback request', 'feedback',
                     sender=sender if sender else None,
                     message=form.message.data, source_url=form.source_url.data)
        flash('Thank you for your feedback! If you included your email, I will respond soon.', 'success')
        return redirect(url_for('home.index'))
    return render_template('feedback.html', form=form)
