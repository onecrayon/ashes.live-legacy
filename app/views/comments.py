"""Comment editing and moderation"""

from flask import abort, Blueprint, flash, redirect, render_template
from flask_login import current_user, login_required

from app import db
from app.models.comment import Comment
from app.models.stream import Stream
from app.models.user import User
from app.views.forms.comment import CommentForm, DeleteForm, ModerateCommentForm
from app.wrappers import admin_required

mod = Blueprint('comments', __name__, url_prefix='/comments')


def verify_comment(comment_id, is_admin=False):
    comment = Comment.query.get_or_404(comment_id)
    if (is_admin and not current_user.is_admin) or (not current_user.is_admin and (
            comment.user_id != current_user.id or comment.is_deleted or comment.is_moderated)):
        abort(404)
    return comment


@mod.route('/<int:comment_id>/', methods=['GET', 'POST'])
@login_required
def edit(comment_id):
    comment = verify_comment(comment_id)
    comment_form = CommentForm(obj=comment)
    if comment_form.cancel.data:
        return redirect(comment.url, code=303)
    if not comment_form.preview.data and comment_form.validate_on_submit():
        comment.text = comment_form.text.data
        db.session.commit()
        flash('Comment updated!', 'success')
        return redirect(comment.url, code=303)
    return render_template('comments/edit.html', comment_form=comment_form)


@mod.route('/<int:comment_id>/delete/', methods=['GET', 'POST'])
@login_required
def delete(comment_id):
    comment = verify_comment(comment_id)
    delete_form = DeleteForm()
    if delete_form.delete_comment.data:
        comment.is_deleted = True
        db.session.query(Stream).filter(
            Stream.entity_id == comment.entity_id
        ).delete(synchronize_session=False)
        db.session.commit()
        flash('Comment deleted!', 'success')
        return redirect(comment.url, code=303)
    elif delete_form.cancel.data:
        return redirect(comment.url, code=303)
    return render_template('comments/delete.html', comment=comment, delete_form=delete_form)


@mod.route('/<int:comment_id>/notes/')
@login_required
def notes(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if not comment or not comment.is_moderated or comment.user_id != current_user.id:
        abort(404)
    return render_template('comments/notes.html', comment=comment)


@mod.route('/<int:comment_id>/moderate/', methods=['GET', 'POST'])
@admin_required
def moderate(comment_id):
    if not current_user.is_admin:
        abort(404)
    comment = verify_comment(comment_id, is_admin=True)
    user = User.query.get(comment.user_id)
    comment_form = ModerateCommentForm(obj=comment)
    if comment_form.validate_on_submit():
        if comment_form.undo_moderation.data:
            # Completely undo all moderation
            comment.text = comment.original_text
            comment.original_text = None
            comment.is_deleted = False
            comment.is_moderated = False
            comment.moderation_notes = None
            db.session.commit()
            flash('Moderation has been reversed.', 'warning')
            return redirect(comment.url, code=303)
        if not comment.original_text:
            comment.original_text = comment.text
        comment.text = comment_form.text.data
        comment.is_deleted = comment_form.is_deleted.data
        comment.is_moderated = True
        comment.moderation_notes = comment_form.moderation_notes.data
        db.session.commit()
        flash('Comment has been moderated.', 'success')
        return redirect(comment.url, code=303)
    return render_template('comments/moderate.html', comment=comment, comment_form=comment_form,
                           user=user)
