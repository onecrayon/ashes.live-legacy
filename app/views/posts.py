"""Post viewing, editing, and moderation"""
from flask import abort, Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, fresh_login_required, login_required

from app import db
from app.models.post import Post, Section
from app.models.stream import Stream
from app.models.user import User
from app.utils.stream import new_entity
from app.views.forms.post import PostForm, DeletePostForm, ModeratePostForm

mod = Blueprint('posts', __name__, url_prefix='/posts')


def verify_post(post_id, is_admin=False):
	post = Post.query.get_or_404(post_id)
	if (is_admin and not current_user.is_admin) or (not current_user.is_admin and (
			post.user_id != current_user.id or post.is_deleted or post.is_moderated)):
		abort(404)
	return post


def get_section_choices():
	query = Section.query
	if not current_user.is_admin:
		query = query.filter(
			Section.is_restricted.is_(False)
		)
	return [(x.id, x.title) for x in query.all()]


@mod.route('/')
def index():
	"""List all available sections"""
	pass


@mod.route('/<stub>/')
@mod.route('/<stub>/<int:page>/')
def section(stub, page=None):
	"""List posts in a particular section"""
	pass


@mod.route('/<int:post_id>/')
def view(post_id):
	"""View a particular post"""
	pass


@mod.route('/submit/', methods=['GET', 'POST'])
@mod.route('/submit/<section_stub>/', methods=['GET', 'POST'])
@login_required
def submit(section_stub=None):
	"""Submit a new post"""
	post_form = PostForm()
	section_tuples = get_section_choices()
	post_form.section.choices = section_tuples
	post_form.section.default = section_tuples[0][0]
	if section_stub:
		post_form.section.data = section_stub
	section = Section.query.filter(
		Section.stub == post_form.section.data,
		Section.is_restricted.is_(False) if not current_user.is_admin else None
	).first()
	if not post_form.preview.data and post_form.validate_on_submit():
		if not section:
			flash('Post submitted to invalid section; please try again.', 'error')
			return redirect(url_for('posts.submit'), title=post_form.title.data,
							text=post_form.text.data)
		post = Post(
			entity_id=new_entity(),
			user_id=current_user.id,
			section_id=section.id,
			title=post_form.title.data,
			text=post_form.text.data
		)
		db.session.add(post)
		db.session.commit()
		flash('Post submitted!', 'success')
		return redirect(url_for('posts.view', post_id=post.id), code=303)
	return render_template(
		'posts/submit.html',
		post_form=post_form,
		section=section if section_stub else None
	)


@mod.route('/<int:post_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit(post_id):
	post = verify_post(post_id)
	post_form = PostForm(obj=post)
	if post_form.cancel.data:
		return redirect(url_for('posts.view', post_id=post_id), code=303)
	if not post_form.preview.data and post_form.validate_on_submit():
		post.title = post_form.title.data
		post.text = post_form.text.data
		db.session.commit()
		flash('Post updated!', 'success')
		return redirect(url_for('posts.view', post_id=post_id), code=303)
	return render_template('posts/edit.html', post_form=post_form)


@mod.route('/<int:post_id>/delete/', methods=['GET', 'POST'])
@login_required
def delete(post_id):
	post = verify_post(post_id)
	delete_form = DeletePostForm()
	if delete_form.delete_post.data:
		post.is_deleted = True
		db.session.query(Stream).filter(
			Stream.entity_id == post.entity_id
		).delete(synchronize_session=False)
		db.session.commit()
		flash('Post deleted!', 'success')
		return redirect(url_for('posts.view', post_id=post_id), code=303)
	elif delete_form.cancel.data:
		return redirect(url_for('posts.view', post_id=post_id), code=303)
	return render_template('posts/delete.html', post=post, delete_form=delete_form)


@mod.route('/<int:post_id>/notes/')
@login_required
def notes(post_id):
	post = verify_post(post_id)
	if not post.is_moderated:
		abort(404)
	return render_template('posts/notes.html', post=post)


@mod.route('/<int:pos_id>/moderate/', methods=['GET', 'POST'])
@fresh_login_required
def moderate(post_id):
	post = verify_post(post_id, is_admin=True)
	user = User.query.get(post.user_id)
	post_form = ModeratePostForm(obj=post)
	if post_form.validate_on_submit():
		if post_form.undo_moderation.data:
			# Completely undo all moderation
			post.title = post.original_title
			post.original_title = None
			post.text = post.original_text
			post.original_text = None
			post.is_deleted = False
			post.is_moderated = False
			post.moderation_notes = None
			db.session.commit()
			flash('Moderation has been reversed.', 'warning')
			return redirect(url_for('posts.view', post_id=post_id), code=303)
		if not post.original_text:
			post.original_text = post.text
		if not post.original_title:
			post.original_title = post.title
		post.title = post_form.title.data
		post.text = post_form.text.data
		post.is_deleted = post_form.is_deleted.data
		post.is_moderated = True
		post.moderation_notes = post_form.moderation_notes.data
		db.session.commit()
		flash('Post has been moderated.', 'success')
		return redirect(url_for('posts.view', post_id=post_id), code=303)
	return render_template('posts/moderate.html', post=post, post_form=post_form,
						   user=user)
