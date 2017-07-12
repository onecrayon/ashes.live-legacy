"""Login/logout and account creation"""

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from application import login_manager
from application.forms.player import InviteForm, LoginForm
from application.models.user import User

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
    """Create account page"""
    form = InviteForm()
    if current_user.is_authenticated:
        return redirect(url_for('index.landing_page'))
    if form.validate_on_submit():
        # TODO: create invite token and email the user
        flash(
            'Invitation sent! Please check your email to finalize your account.',
            'success'
        )
        return redirect(url_for('player.login'))
    return render_template('player/new.html', form=form)


@mod.route('/verify/<uuid:token>/')
def verify(token):
    """Verifies a player's email address, finalizes their account, and logs them in"""
    pass
