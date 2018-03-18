import math

from flask import current_app, redirect, url_for
from flask_login import current_user

from app import db
from app.exceptions import Redirect
from app.models.comment import Comment
from app.utils import get_pagination
from app.utils.stream import new_entity, refresh_entity
from app.views.forms.comment import CommentForm


def get_comments(entity_id, page=None):
    """Returns a list of comments for the given entity_id"""
    if not page:
        page = 1
    per_page = current_app.config['DEFAULT_PAGED_RESULTS']
    query = db.session.query(Comment).options(
        db.joinedload('user')
    ).filter(
        Comment.source_entity_id == entity_id
    )
    comments = query.order_by(Comment.order.asc()).limit(per_page).offset(
        (page - 1) * per_page
    ).all()
    pagination = get_pagination(query.count(), page, per_page)
    return comments, pagination


def process_comments(entity_id, source_type='deck', page=None):
    # Only authenticated users may submit comments
    if not current_user.is_authenticated:
        comments, pagination = get_comments(entity_id, page=page)
        return comments, pagination, None
    comment_form = CommentForm(source_entity_id=entity_id, source_type=source_type)
    if not comment_form.preview.data and comment_form.validate_on_submit():
        # Save the comment!
        comment = Comment(
            entity_id=new_entity(),
            user_id=current_user.id,
            source_entity_id=comment_form.source_entity_id.data,
            source_type=comment_form.source_type.data,
            text=comment_form.text.data,
        )
        order = db.session.query(Comment.order).filter(
            Comment.source_entity_id == comment.source_entity_id
        ).order_by(Comment.created.desc()).limit(1).scalar()
        comment.order = order + 1 if order else 1
        db.session.add(comment)
        db.session.commit()
        refresh_entity(comment.entity_id, entity_type='comment')
        raise Redirect(comment.url, status_code=303)
    comments, pagination = get_comments(entity_id, page=page)
    return comments, pagination, comment_form
