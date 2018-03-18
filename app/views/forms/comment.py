from flask_wtf import FlaskForm
from wtforms import HiddenField, TextAreaField
from wtforms.validators import DataRequired


class CommentForm(FlaskForm):
    source_entity_id = HiddenField()
    source_type = HiddenField()
    text = TextAreaField('Comment', validators=[DataRequired()])
