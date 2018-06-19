"""Index/landing page for the site"""

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from app import db
from app.models.deck import Deck
from app.utils import send_message
from app.utils.ashes_500 import latest_ashes_500_revision
from app.utils.posts import get_pinned_posts
from app.utils.stream import get_stream
from app.views.forms.feedback import FeedbackForm

mod = Blueprint('home', __name__)


@mod.route('/')
@mod.route('/<int:page>/')
def index(page=None):
    showing = request.args.get('show', 'all')
    stream, page, pagination = get_stream(page=page, show=showing)
    pinned = get_pinned_posts() if page == 1 else None
    latest_ashes_500 = latest_ashes_500_revision()
    return render_template(
        'index.html',
        pinned=pinned,
        stream=stream,
        latest_ashes_500=latest_ashes_500,
        page=page,
        pages=pagination,
        showing=showing
    )


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


@mod.route('/content-policies/')
def policies():
    """Static page: content policies"""
    return render_template('content-policies.html')
