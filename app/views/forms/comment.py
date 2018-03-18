from flask_wtf import FlaskForm
from wtforms import HiddenField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class CommentForm(FlaskForm):
    source_entity_id = HiddenField()
    source_type = HiddenField()
    text = TextAreaField('Comment', validators=[DataRequired()])
    preview = SubmitField('Preview', render_kw={
        'class': 'btn',
        'formaction': './#comment-preview'
    })
