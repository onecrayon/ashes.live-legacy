from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField


class SnapshotForm(FlaskForm):
    title = StringField('Title')
    description = TextAreaField('Description')
