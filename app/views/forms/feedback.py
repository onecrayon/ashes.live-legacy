from flask import request
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Optional

class FeedbackForm(FlaskForm):
    source_url = HiddenField()
    email = StringField('Email', validators=[
        Optional(),
        Email(message='Invalid email.')
    ])
    message = TextAreaField('Message', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        if current_user.is_authenticated:
            self.email.data = current_user.email
        if not self.source_url.data:
            self.source_url.data = request.referrer
