from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


cancel_button = SubmitField('Cancel', render_kw={
    'class': 'btn float-right'
})


class PostForm(FlaskForm):
    section_stub = SelectField('Section', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    text = TextAreaField('Text', validators=[DataRequired()])
    preview = SubmitField('Preview', render_kw={
        'class': 'btn',
        'formaction': './#post-preview'
    })
    cancel = cancel_button


class DeletePostForm(FlaskForm):
    delete_post = SubmitField('Delete Post', render_kw={
        'class': 'btn btn-danger'
    })
    cancel = cancel_button


class ModeratePostForm(PostForm):
    moderation_notes = TextAreaField('Reason for moderation', validators=[DataRequired()])
    is_deleted = BooleanField('Delete post')
    undo_moderation = SubmitField('Undo Moderation', render_kw={
        'class': 'btn btn-danger'
    })


class PinPostForm(FlaskForm):
    pin_teaser = TextAreaField('Teaser Text', validators=[DataRequired()])
    cancel = cancel_button


class SectionForm(FlaskForm):
    description = TextAreaField('Description', validators=[DataRequired()])
    preview = SubmitField('Preview', render_kw={
        'class': 'btn',
        'formaction': './#preview'
    })
    cancel = cancel_button
