"""Login/logout and account creation"""

from flask import Blueprint
from flask_login import login_required

mod = Blueprint('player', __name__, url_prefix='/player')


@mod.route('/')
@login_required
def player_account():
    """Edit current player's account"""
    pass


@mod.route('/<player_badge>/')
def player_profile(player_badge):
    """View a player's public profile"""
    pass


@mod.route('/login/', methods=['GET', 'POST'])
def login():
    """Log a player into the site"""
    pass


@mod.route('/logout/')
@login_required
def logout():
    """Log a player out"""
    pass


@mod.route('/new/', methods=['GET', 'POST'])
def new_player():
    """Create account page"""
    pass


@mod.route('/verify/<uuid:token>/')
def verify_player(token):
    """Verifies a player's email address and logs them in"""
    pass
