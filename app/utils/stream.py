from collections import defaultdict
from datetime import datetime

from flask import current_app, url_for
from flask_login import current_user

from app import db
from app.models.comment import Comment
from app.models.deck import Deck
from app.models.post import Post
from app.models.stream import Stream, Streamable, Subscription
from app.models.user import User
from app.utils import get_pagination, send_message


def new_entity():
    """Creates a new Streamable entity and returns the ID"""
    entity = Streamable()
    db.session.add(entity)
    db.session.commit()
    return entity.entity_id


def user_to_entity_map(user):
    return {
        'badge': user.badge,
        'username': user.username
    }


def deck_to_entity_map(deck):
    return {
        'user': user_to_entity_map(deck.user),
        'created': deck.created,
        'source_id': deck.source_id,
        'title': deck.title,
        'phoenixborn': {
            'name': deck.phoenixborn.name,
            'stub': deck.phoenixborn.stub
        },
        'dice': deck.dice,
        'ashes_500_score': deck.ashes_500_score if deck.ashes_500_revision_id else None,
        'url': url_for('decks.view', deck_id=deck.source_id),
        'unsubscribe_url': url_for('decks.subscribe', deck_id=deck.source_id)
    }


def post_to_entity_map(post):
    return {
        'user': user_to_entity_map(post.user),
        'user_id': post.user.id,
        'section': {
            'title': post.section.title,
            'stub': post.section.stub
        },
        'id': post.id,
        'created': post.created,
        'modified': post.modified,
        'is_moderated': post.is_moderated,
        'title': post.title,
        'text': post.text,
        'url': url_for('posts.view', post_id=post.id),
        'unsubscribe_url': url_for('posts.subscribe', post_id=post.id)
    }


def comment_to_entity_map(comment):
    source_title = None
    unsubscribe_url = None
    if comment.source_type == 'card':
        source_title = comment.source.name
        unsubscribe_url = url_for('cards.subscribe', stub=comment.source.stub)
    elif comment.source_type == 'deck':
        snapshot = comment.source.published_snapshot()
        source_title = snapshot.title if snapshot else None
        unsubscribe_url = url_for('decks.subscribe', deck_id=comment.source.id)
    elif comment.source_type == 'post':
        source_title = comment.source.title
        unsubscribe_url = url_for('posts.subscribe', post_id=comment.source.id)
    return {
        'user': user_to_entity_map(comment.user),
        'created': comment.created,
        'text': comment.text,
        'source_title': source_title,
        'source_type': comment.source_type,
        'url': comment.url,
        'unsubscribe_url': unsubscribe_url
    }


def refresh_entity(entity_id, entity_type, source_entity_id):
    if entity_type == 'deck':
        entity = db.session.query(Stream).filter(
            Stream.source_entity_id == source_entity_id
        ).first()
    else:
        entity = db.session.query(Stream).filter(Stream.entity_id == entity_id).first()
    if not entity:
        entity = Stream(entity_id=entity_id, entity_type=entity_type,
                        source_entity_id=source_entity_id)
    elif entity_type == 'deck':
        # Decks are a special case; we update the Stream entity because the snapshots effectively
        # replace one another as far as most users are concerned
        entity.posted = datetime.utcnow()
        entity.entity_id = entity_id
    else:
        # Ignore comment edits
        return
    db.session.add(entity)
    # Grab users who are subscribed to this and have email notifications on
    emails = db.session.query(User.email).join(
        Subscription, Subscription.user_id == User.id
    ).filter(
        User.id != current_user.id,
        User.email_subscriptions.is_(True),
        Subscription.source_entity_id == source_entity_id
    ).all()
    if not emails:
        return
    recipients = [x.email for x in emails]
    entity_map = {
        'entity_type': entity_type
    }
    subject = ''
    if entity_type == 'deck':
        deck = db.session.query(Deck).options(
            db.joinedload('phoenixborn'),
            db.joinedload('dice'),
            db.joinedload('user')
        ).filter(
            entity_id == entity_id,
            Deck.is_snapshot.is_(True),
            Deck.is_public.is_(True)
        ).first()
        if not deck:
            return
        entity_map.update(deck_to_entity_map(deck))
        subject = "Deck updated: '{}'".format(entity_map['title'])
    elif entity_type == 'post':
        post = db.session.query(Post).options(
            db.joinedload('user'),
            db.joinedload('section')
        ).filter(
            Post.entity_id == entity_id
        ).first()
        if not post:
            return
        entity_map.update(post_to_entity_map(post))
        subject = "New post '{}'".format(entity_map['title'])
    else:
        comment = db.session.query(Comment).options(
            db.joinedload('user')
        ).filter(
            Comment.entity_id == entity_id
        ).first()
        if not comment:
            return
        entity_map.update(comment_to_entity_map(comment))
        subject = "New comment on the {} '{}'".format(
            entity_map['source_type'],
            entity_map['source_title']
        )
    # Limit subjects to 78 characters
    if len(subject) > 78:
        subject = subject[0:74] + "...'"
    send_message(recipients, subject, 'subscription', entity=entity_map)



def update_subscription(source_entity_id, last_seen_entity_id=None):
    subscription = db.session.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.source_entity_id == source_entity_id
    ).first()
    if not subscription:
        subscription = Subscription(
            user_id=current_user.id,
            source_entity_id=source_entity_id,
            last_seen_entity_id=last_seen_entity_id
        )
    else:
        subscription.last_seen_entity_id = last_seen_entity_id
    db.session.add(subscription)


def toggle_subscription(source_entity_id, fallback_last_seen=None):
    subscription = db.session.query(Subscription).filter(
        Subscription.source_entity_id == source_entity_id,
        Subscription.user_id == current_user.id
    ).first()
    if subscription:
        db.session.delete(subscription)
    else:
        comment = db.session.query(Comment.entity_id).filter(
            Comment.source_entity_id == source_entity_id
        ).order_by(Comment.entity_id.desc()).first()
        last_seen_entity_id = comment.entity_id if comment else None
        if not last_seen_entity_id and fallback_last_seen:
            last_seen_entity_id = fallback_last_seen
        db.session.add(Subscription(
            source_entity_id=source_entity_id,
            user_id=current_user.id,
            last_seen_entity_id=last_seen_entity_id
        ))
    db.session.commit()


def next_subscription_link():
    next_subscription_link = None
    if not current_user.is_authenticated:
        return next_subscription_link
    stream_entity = db.session.query(Stream).join(
        Subscription, db.and_(
            Subscription.source_entity_id == Stream.source_entity_id,
            Subscription.user_id == current_user.id
        )
    ).filter(
        db.or_(
            Subscription.last_seen_entity_id.is_(None),
            Stream.entity_id > Subscription.last_seen_entity_id
        )
    ).order_by(Stream.posted.asc()).first()
    if not stream_entity:
        return next_subscription_link
    if stream_entity.entity_type == 'comment':
        comment = db.session.query(Comment).filter(
            Comment.entity_id == stream_entity.entity_id
        ).first()
        next_subscription_link = comment.url
    elif stream_entity.entity_type == 'deck':
        deck = db.session.query(Deck.id).filter(
            Deck.entity_id == stream_entity.source_entity_id
        ).first()
        next_subscription_link = url_for('decks.view', deck_id=deck.id)
    return next_subscription_link


def get_stream(page=None, show='all'):
    """Returns a stream of site entities and pagination information"""
    if not page:
        page = 1
    per_page = current_app.config['DEFAULT_PAGED_RESULTS']
    user_id = current_user.id if current_user.is_authenticated else None
    stream_query = db.session.query(
        Stream,
        Subscription
    ).outerjoin(
        Subscription, db.and_(
            Subscription.source_entity_id == Stream.source_entity_id,
            Subscription.user_id == user_id
        )
    )
    if current_user.is_authenticated and current_user.exclude_subscriptions:
        stream_query = stream_query.filter(
            db.or_(
                Stream.entity_type != 'comment',
                Subscription.source_entity_id.is_(None)
            )
        )
    if show != 'all':
        stream_query = stream_query.filter(
            # Show is always plural, so strip off the trailing 's'
            Stream.entity_type == show[:-1]
        )
    stream = stream_query.order_by(Stream.posted.desc()).limit(per_page).offset(
        (page - 1) * per_page
    ).all()
    deck_entity_ids = set()
    post_entity_ids = []
    comment_entity_ids = []
    entity_map = {}
    for entity, subscription in stream:
        if entity.entity_type == 'deck':
            deck_entity_ids.add(entity.source_entity_id)
        elif entity.entity_type == 'post':
            post_entity_ids.append(entity.entity_id)
        else:
            comment_entity_ids.append(entity.entity_id)
        entity_map[entity.entity_id] = {
            'entity_type': entity.entity_type,
            'is_unread': (
                not subscription.last_seen_entity_id or
                entity.entity_id > subscription.last_seen_entity_id if subscription
                else False
            )
        }
    # Gather the latest public snapshots for all decks in the stream
    if deck_entity_ids:
        snapshot_comp = db.aliased(Deck)
        source_comp = db.aliased(Deck)
        decks = db.session.query(Deck).options(
            db.joinedload('phoenixborn'),
            db.joinedload('dice'),
            db.joinedload('user')
        ).join(
            source_comp, source_comp.id == Deck.source_id
        ).outerjoin(snapshot_comp, db.and_(
            Deck.source_id == snapshot_comp.source_id,
            snapshot_comp.is_snapshot.is_(True),
            snapshot_comp.is_public.is_(True),
            Deck.created < snapshot_comp.created
        )).filter(
            source_comp.entity_id.in_(list(deck_entity_ids)),
            snapshot_comp.id.is_(None),
            Deck.is_snapshot.is_(True),
            Deck.is_public.is_(True)
        ).all()
        for deck in decks:
            entity_map[deck.entity_id].update(deck_to_entity_map(deck))
    # Gather posts
    if post_entity_ids:
        posts = db.session.query(Post).options(
            db.joinedload('user'),
            db.joinedload('section')
        ).filter(
            Post.entity_id.in_(post_entity_ids)
        ).all()
        for post in posts:
            entity_map[post.entity_id].update(post_to_entity_map(post))
    # Gather comments
    if comment_entity_ids:
        comments = db.session.query(Comment).options(
            db.joinedload('user')
        ).filter(
            Comment.entity_id.in_(comment_entity_ids)
        ).all()
        for comment in comments:
            entity_map[comment.entity_id].update(comment_to_entity_map(comment))
    pagination = get_pagination(stream_query.count(), page, per_page)
    return [entity_map[x.Stream.entity_id] for x in stream], page, pagination
