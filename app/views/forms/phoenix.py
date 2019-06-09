from flask import request
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, StringField
from wtforms.validators import DataRequired, Email, NumberRange

class InterestForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Invalid email.')
    ])
    desired_sets = IntegerField('Desired sets (10 dice per set)', validators=[
        NumberRange(1, 50)
    ], default=1, render_kw={'type': 'number'})
    only_official_icons = BooleanField('I would only buy physical dice with the official icons')
