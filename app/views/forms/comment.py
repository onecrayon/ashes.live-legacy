from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired


cancel_button = SubmitField('Cancel', render_kw={
    'class': 'btn float-right'
})


class CommentForm(FlaskForm):
    text = TextAreaField('Comment', validators=[DataRequired()])
    preview = SubmitField('Preview', render_kw={
        'class': 'btn',
        'formaction': './#comment-preview'
    })
    cancel = cancel_button


class DeleteForm(FlaskForm):
    delete_comment = SubmitField('Delete Comment', render_kw={
        'class': 'btn btn-danger'
    })
    cancel = cancel_button


class ModerateCommentForm(CommentForm):
    moderation_notes = TextAreaField('Moderation Notes', validators=[DataRequired()])
    delete_comment = SubmitField('Delete Comment', render_kw={
        'class': 'btn btn-error'
    })
    cancel = cancel_button
