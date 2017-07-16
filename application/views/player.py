"""Login/logout and account creation"""

from flask import abort, Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message

from application import db, login_manager
from application.models.invite import Invite
from application.models.user import User
from application.views.forms.player import CreateForm, EmailForm, LoginForm, ResetForm
from application.utils import send_message
from application.wrappers import guest_required

mod = Blueprint('player', __name__, url_prefix='/player')


# Configure login behavior
login_manager.login_view = 'player.login'
login_manager.login_message = None

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@mod.route('/')
@login_required
def account():
    """Edit current player's account"""
    pass


@mod.route('/<badge>/')
def view(badge):
    """View a player's public profile"""
    badge = badge.lower()
    user = User.query.filter(User.badge == badge).first()
    if not user:
        return abort(404)
    return render_template('player/view.html', user=user)


@mod.route('/login/', methods=['GET', 'POST'])
@guest_required
def login():
    """Log a player into the site"""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.log_in(form.email.data, form.password.data)
        if user:
            login_user(user, remember=form.remember_me.data)
            # Redirect logic handles `next` forwarding
            return form.redirect('home.index')
        else:
            flash('Incorrect email or password.', 'error')
    return render_template('player/login.html', form=form)


@mod.route('/logout/')
@login_required
def logout():
    """Log a player out"""
    logout_user()
    return redirect(url_for('home.index'))


def request_invite():
    form = EmailForm()
    if form.validate_on_submit():
        # Make sure we do not have any users with this email in the database
        user = User.query.filter(User.email == form.email.data).first()
        if user:
            flash('This email is already in use; <a href="{}">reset your password</a>?'.format(
            	url_for('player.reset')
            ), 'error')
            return render_template('player/new_invite.html', form=form)
        # Grab our invitation info
        invitation = Invite.get_for_email(form.email.data)
        # Email the user
        send_message(
            invitation.email, 'Create your Ashes.live account!', 'invite_token',
            invite=invitation
        )
        return render_template('player/invite_sent.html', email=form.email.data)
    return render_template('player/new_invite.html', form=form)


def create_account(uuid):
    """Creates account page; accessed via emailed verification link"""
    invitation = Invite.query.get(uuid)
    if not invitation:
        flash('Your account invitation URL has expired; you can resend it below.', 'error')
        return redirect(url_for('player.new'))
    if not session.get('badge_choices'):
        session['badge_choices'] = [(x, '#{}'.format(x)) for x in User.fetch_badges(number=9)]
    form = CreateForm()
    form.badge.choices = session['badge_choices']
    form.badge.default = session['badge_choices'][0][0]
    # Have to process the form in order for the default to take effect
    form.process(request.form)
    form.email.data = invitation.email
    if form.validate_on_submit():
        # Create our user account
        user = User(
            email=form.email.data,
            password=form.password.data,
            badge=form.badge.data,
            username=form.username.data,
            newsletter_opt_in=form.newsletter.data
        )
        db.session.add(user)
        # Delete the invitation and session badges
        db.session.delete(invitation)
        session.pop('badge_choices', None)
        # Commit our changes
        db.session.commit()
        # Login, and redirect to the homepage
        login_user(user)
        flash('Welcome to Ashes.live!', 'success')
        return redirect(url_for('home.index'))
    return render_template('player/new.html', form=form)


@mod.route('/new/', methods=['GET', 'POST'])
@mod.route('/new/<uuid>/', methods=['GET', 'POST'])
@guest_required
def new(uuid=None):
    """Create account page"""
    if uuid is None:
        return request_invite()
    return create_account(uuid)


def request_reset():
    form = EmailForm()
    if form.validate_on_submit():
        # Make sure we have a user with this email in the database
        user = User.query.filter(User.email == form.email.data).first()
        if not user:
            flash('No account found; <a href="{}">create your account</a>?'.format(
            	url_for('player.new')
            ), 'error')
            return render_template('player/reset_request.html', form=form)
        # Mark account for password reset
        user.generate_reset_uuid()
        # Email the user
        send_message(
            user.email, 'Reset your Ashes.live password', 'reset_token',
            user=user
        )
        return render_template('player/reset_sent.html', email=form.email.data)
    return render_template('player/reset_request.html', form=form)


def change_password(uuid):
    user = User.query.filter(User.reset_uuid == uuid).first()
    if not user:
        flash('Your reset URL has expired; you can resend it below.', 'error')
        return redirect(url_for('player.reset'))
    form = ResetForm()
    if form.validate_on_submit():
        # Reset the user's password
        user.set_password(form.password.data)
        login_user(user)
        flash('Password successfully reset!', 'success')
        return redirect(url_for('home.index'))
    return render_template('player/reset.html', form=form)


@mod.route('/reset/', methods=['GET', 'POST'])
@mod.route('/reset/<uuid>/', methods=['GET', 'POST'])
@guest_required
def reset(uuid=None):
    """Reset account password"""
    if uuid is None:
        return request_reset()
    return change_password(uuid)
