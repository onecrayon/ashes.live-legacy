"""Login/logout and account creation"""

from flask import Blueprint, flash, redirect, render_template, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message

from application import login_manager
from application.forms.player import CreateForm, EmailForm, LoginForm
from application.models.invite import Invite
from application.models.user import User
from application.utils import send_message

mod = Blueprint('player', __name__, url_prefix='/player')


# Configure login behavior
login_manager.login_view = 'player.login'
login_manager.login_message = None

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@mod.route('/')
@login_required
def account():
    """Edit current player's account"""
    pass


@mod.route('/<player_badge>/')
def view_profile(player_badge):
    """View a player's public profile"""
    pass


@mod.route('/login/', methods=['GET', 'POST'])
def login():
    """Log a player into the site"""
    form = LoginForm()
    if current_user.is_authenticated:
        return form.redirect('index.landing_page')
    if form.validate_on_submit():
        user = User.log_in(form.email.data, form.password.data)
        if user:
            login_user(user, remember=form.remember_me.data)
            # Redirect logic handles `next` forwarding
            return form.redirect('index.landing_page')
        else:
            flash('Incorrect email or password.', 'error')
    return render_template('player/login.html', form=form)


@mod.route('/logout/')
@login_required
def logout():
    """Log a player out"""
    logout_user()
    return redirect(url_for('index.landing_page'))


@mod.route('/new/', methods=['GET', 'POST'])
def new():
    """Request account page"""
    form = EmailForm()
    if current_user.is_authenticated:
        return redirect(url_for('index.landing_page'))
    if form.validate_on_submit():
        # Make sure we do not have any users with this email in the database
        user = User.query.filter(User.email == form.email.data).first()
        if user:
            flash('This email is already in use; <a href="{}">reset your password</a>?'.format(
            	url_for('player.reset')
            ), 'error')
            return render_template('player/new.html', form=form)
        # Grab our invitation info
        invitation = Invite.get_for_email(form.email.data)
        # Email the user
        send_message(
            invitation.email, 'Create your Ashes.live account!', 'invite_token',
            invite=invitation
        )
        return render_template('player/invite_sent.html', email=form.email.data)
    return render_template('player/new.html', form=form)


@mod.route('/create/<string:uuid>/', methods=['GET', 'POST'])
def create(uuid):
    """Creates account page; accessed via emailed verification link"""
    if current_user.is_authenticated:
        return redirect(url_for('index.landing_page'))
    invitation = Invite.query.get(uuid)
    if not invitation:
        flash('Your account invitation URL has expired; you can resend it below.', 'error')
        return redirect(url_for('player.new'))
    if not session.get('badge_choices'):
        session['badge_choices'] = [(x, '#{}'.format(x)) for x in User.fetch_badges(maximum=9)]
    form = CreateForm()
    form.badge.choices = session['badge_choices']
    form.badge.default = session['badge_choices'][0][0]
    # Have to process the form in order for the default to take effect
    form.process()
    # Have to set email after re-processing, because processing clears it
    form.email.data = invitation.email
    if form.validate_on_submit():
        # TODO: create our user account and log them in
        pass
    return render_template('player/create.html', form=form)


@mod.route('/reset/', methods=['GET', 'POST'])
def reset():
    """Reset account password"""
    pass
