"""Project Phoenix information page"""

from flask import Blueprint, flash, render_template
from flask_login import current_user

from app import db
from app.views.forms.phoenix import InterestForm
from app.models.phoenix_dice import PhoenixDice

mod = Blueprint('phoenix', __name__, url_prefix='/phoenix')


@mod.route('/')
def index():
    return render_template('phoenix/index.html')


@mod.route('/dice/', methods=['GET', 'POST'])
def dice():
    """Survey folks for interest in physical dice"""
    form = InterestForm(data={'email': current_user.email} if current_user.is_authenticated else {})
    if form.validate_on_submit():
        email = form.email.data
        interest = PhoenixDice.query.filter(PhoenixDice.email == email).first()
        if not interest:
            interest = PhoenixDice(email=email)
        interest.only_official_icons = form.only_official_icons.data
        interest.desired_sets = form.desired_sets.data
        db.session.add(interest)
        db.session.commit()
        flash(
            'Thank you for your interest in Turtle Dice! I will email you '
            'when physical dice are available.',
            'success'
        )
    total_interest = db.session.query(
        db.func.sum(PhoenixDice.desired_sets)
    ).filter(
        PhoenixDice.only_official_icons.is_(False)
    ).scalar()
    total_interest = total_interest if total_interest else 0
    return render_template('phoenix/dice.html', form=form, total_interest=total_interest)
