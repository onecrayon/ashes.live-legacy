"""Comment editing and moderation"""

from flask import abort, Blueprint, flash, redirect, render_template
from flask_login import current_user, login_required

from app import db
from app.models.comment import Comment
from app.views.forms.comment import CommentForm, DeleteForm, ModerateCommentForm

mod = Blueprint('comments', __name__, url_prefix='/comments')


@mod.route('/<int:comment_id>/', methods=['GET', 'POST'])
@login_required
def edit(comment_id):
	comment = Comment.query.get_or_404(comment_id)
	if comment.user_id != current_user.id or comment.is_deleted or comment.is_moderated:
		abort(404)
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
	comment = Comment.query.get_or_404(comment_id)
	if comment.user_id != current_user.id or comment.is_deleted or comment.is_moderated:
		abort(404)
	delete_form = DeleteForm()
	if delete_form.delete_comment.data:
		comment.is_deleted = True
		db.session.commit()
		flash('Comment deleted!', 'success')
		return redirect(comment.url, code=303)
	elif delete_form.cancel.data:
		return redirect(comment.url, code=303)
	return render_template('comments/delete.html', comment=comment, delete_form=delete_form)


@mod.route('/<int:comment_id>/moderate/', methods=['GET', 'POST'])
@login_required
def moderate(comment_id):
	pass
