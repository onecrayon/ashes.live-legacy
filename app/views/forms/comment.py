from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired


class CommentForm(FlaskForm):
    text = TextAreaField('Comment', validators=[DataRequired()])
    preview = SubmitField('Preview', render_kw={
        'class': 'btn',
        'formaction': './#comment-preview'
    })
