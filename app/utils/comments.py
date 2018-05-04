import math

from flask import current_app, redirect, url_for
from flask_login import current_user

from app import db
from app.exceptions import Redirect
from app.models.comment import Comment
from app.models.stream import Subscription
from app.utils import get_pagination
from app.utils.stream import new_entity, refresh_entity, update_subscription
from app.views.forms.comment import CommentForm


def get_comments(entity_id, fallback_last_seen_entity_id=None, page=None):
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
    last_comment_entity_id = comments[-1].entity_id if comments else None
    if fallback_last_seen_entity_id and not last_comment_entity_id:
        last_comment_entity_id = fallback_last_seen_entity_id
    if not current_user.is_authenticated:
        last_seen_entity_id = None
    else:
        subscription = db.session.query(Subscription).filter(
            Subscription.user_id == current_user.id,
            Subscription.source_entity_id == entity_id
        ).first()
        if not subscription:
            last_seen_entity_id = None
        elif not subscription.last_seen_entity_id:
            # This is a bit of a hack to make the entity ID always work in integer comparisons;
            # this entity_id is guaranteed to belong to the first card in the database, and thus
            # is a safe comparison for comments.
            last_seen_entity_id = 1
        else:
            last_seen_entity_id = subscription.last_seen_entity_id
        # Update their subscription now that they've seen this page
        if (subscription and last_comment_entity_id and last_seen_entity_id and
                last_seen_entity_id < last_comment_entity_id):
            subscription.last_seen_entity_id = last_comment_entity_id
            db.session.commit()
    return comments, pagination, last_seen_entity_id


def process_comments(entity_id, source_type='deck', source_version=None, page=None,
                     allow_commenting=True, fallback_last_seen_entity_id=None):
    # Only authenticated users may submit comments
    if not current_user.is_authenticated or not allow_commenting:
        comments, pagination, last_seen_entity_id = get_comments(
            entity_id, fallback_last_seen_entity_id=fallback_last_seen_entity_id, page=page
        )
        return comments, pagination, last_seen_entity_id, None
    comment_form = CommentForm()
    if not comment_form.preview.data and comment_form.validate_on_submit():
        # Save the comment!
        comment = Comment(
            entity_id=new_entity(),
            user_id=current_user.id,
            source_entity_id=entity_id,
            source_type=source_type,
            source_version=source_version,
            text=comment_form.text.data,
        )
        order = db.session.query(Comment.order).filter(
            Comment.source_entity_id == comment.source_entity_id
        ).order_by(Comment.created.desc()).limit(1).scalar()
        comment.order = order + 1 if order else 1
        db.session.add(comment)
        # Add the comment to the Stream
        refresh_entity(comment.entity_id, 'comment', comment.source_entity_id)
        # Subscribe the user to the comment's source
        update_subscription(comment.source_entity_id, comment.entity_id)
        db.session.commit()
        raise Redirect(comment.url, status_code=303)
    comments, pagination, last_seen_entity_id = get_comments(
        entity_id, fallback_last_seen_entity_id=fallback_last_seen_entity_id, page=page
    )
    return comments, pagination, last_seen_entity_id, comment_form
