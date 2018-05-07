"""Post viewing, editing, and moderation"""
from flask import abort, Blueprint, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, fresh_login_required, login_required

from app import db
from app.exceptions import Redirect
from app.models.post import Post, Section
from app.models.stream import Stream, Subscription
from app.models.user import User
from app.utils import get_pagination
from app.utils.comments import process_comments
from app.utils.stream import new_entity, refresh_entity, toggle_subscription, update_subscription
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
    return [(x.stub, x.title) for x in query.all()]


@mod.route('/')
def index():
    """List all available sections"""
    return render_template('posts/index.html', sections=db.session.query(Section).all())


@mod.route('/<stub>/')
@mod.route('/<stub>/<int:page>/')
def section(stub, page=None):
    """List posts in a particular section"""
    section = db.session.query(Section).filter(Section.stub == stub).first()
    if not section:
        abort(404)
    query = db.session.query(Post).options(
        db.joinedload('user'),
        db.joinedload('section')
    ).filter(Post.section_id == section.id)
    # TODO: add filter logic to search for posts by title/text (similar to cards)
    if not page:
        page = 1
    per_page = current_app.config['DEFAULT_PAGED_RESULTS']
    posts = query.order_by(Post.created.desc()).limit(per_page).offset(
        (page - 1) * per_page
    ).all()
    pagination = get_pagination(query.count(), page, per_page)
    if current_user.is_authenticated:
        is_subscribed = db.session.query(Subscription.user_id).filter(
            Subscription.user_id == current_user.id,
            Subscription.source_entity_id == section.entity_id
        ).count()
        unreads = db.session.query(Subscription.source_entity_id).filter(
            Subscription.source_entity_id.in_([x.entity_id for x in posts]),
            Subscription.user_id == current_user.id,
            Subscription.last_seen_entity_id.is_(None)
        ).all() if posts else None
        unreads = [x.source_entity_id for x in unreads] if unreads else []
    else:
        is_subscribed = False
        unreads = []
    # TODO: figure out how to get `is_unread` into the list of posts
    return render_template(
        'posts/section.html',
        section=section,
        posts=posts,
        unread_entity_ids=unreads,
        page=page,
        pages=pagination,
        is_subscribed=is_subscribed
    )


@mod.route('/<stub>/subscribe/')
def subscribe_section(stub):
    """(Un)subscribe to a section"""
    section = db.session.query(Section.entity_id).filter(Section.stub == stub).first()
    if not section:
        abort(404)
    toggle_subscription(section.entity_id)
    return redirect(url_for('posts.section', stub=stub), code=303)


@mod.route('/<int:post_id>/', methods=['GET', 'POST'])
@mod.route('/<int:post_id>/<int:page>/', methods=['GET', 'POST'])
def view(post_id, page=1):
    """View a particular post"""
    post = Post.query.options(
        db.joinedload('user'),
        db.joinedload('section')
    ).get_or_404(post_id)
     # Gather comments
    try:
        comments, pagination, last_seen_entity_id, comment_form = process_comments(
            post.entity_id, source_type='post', page=page
        )
    except Redirect as error:
        return redirect(error.url, code=error.status_code)
    return render_template(
        'posts/view.html',
        post=post,
         # Standard comment properties
        comment_version=0, # Posts are unversioned
        comments=comments,
        comment_last_seen=last_seen_entity_id,
        pagination_options={
            'view_path': 'posts.view',
            'pages': pagination,
            'post_id': post_id,
            'page': page
        },
        comment_form=comment_form
    )


@mod.route('/<int:post_id>/subscribe/')
def subscribe(post_id):
    """(Un)subscribe to a particular post"""
    post = db.session.query(Post.entity_id).filter(Post.id == post_id).first()
    if not post:
        abort(404)
    toggle_subscription(post.entity_id)
    return redirect(url_for('posts.view', post_id=post_id), code=303)


@mod.route('/submit/', methods=['GET', 'POST'])
@mod.route('/<section_stub>/submit/', methods=['GET', 'POST'])
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
        Section.stub == post_form.section.data
    )
    if not current_user.is_admin:
        section = section.filter(Section.is_restricted.is_(False))
    section = section.first()
    if post_form.cancel.data:
        if not section_stub:
            return redirect(url_for('home.index'), code=303)
        else:
            return redirect (url_for('posts.section', stub=section_stub), code=303)
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
        refresh_entity(post.entity_id, 'post', section.entity_id,
                       section_entity_id=section.entity_id)
        # Subscribe the user to the post
        update_subscription(post.entity_id)
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
    post_form.section.choices = get_section_choices()
    if post_form.cancel.data:
        return redirect(url_for('posts.view', post_id=post_id), code=303)
    if not post_form.preview.data and post_form.validate_on_submit():
        post.title = post_form.title.data
        post.text = post_form.text.data
        db.session.commit()
        flash('Post updated!', 'success')
        return redirect(url_for('posts.view', post_id=post_id), code=303)
    return render_template('posts/edit.html', post_form=post_form, section=post.section)


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


@mod.route('/<int:post_id>/moderate/', methods=['GET', 'POST'])
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
