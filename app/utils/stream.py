from collections import defaultdict
from datetime import datetime

from flask import current_app
from flask_login import current_user

from app import db
from app.models.comment import Comment
from app.models.deck import Deck
from app.models.stream import Stream, Streamable, Subscription
from app.utils import get_pagination


def new_entity():
    """Creates a new Streamable entity and returns the ID"""
    entity = Streamable()
    db.session.add(entity)
    db.session.commit()
    return entity.entity_id


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


def get_stream(page=None):
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
    stream = stream_query.order_by(Stream.posted.desc()).limit(per_page).offset(
        (page - 1) * per_page
    ).all()
    deck_entity_ids = set()
    comment_entity_ids = []
    entity_map = {}
    for entity, subscription in stream:
        if entity.entity_type == 'deck':
            deck_entity_ids.add(entity.source_entity_id)
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
            entity_map[deck.entity_id].update({
                'user': {
                    'badge': deck.user.badge,
                    'username': deck.user.username
                },
                'created': deck.created,
                'source_id': deck.source_id,
                'title': deck.title,
                'phoenixborn': {
                    'name': deck.phoenixborn.name,
                    'stub': deck.phoenixborn.stub
                },
                'dice': deck.dice
            })
    # Gather comments
    if comment_entity_ids:
        comments = db.session.query(Comment).options(
            db.joinedload('user')
        ).filter(
            Comment.entity_id.in_(comment_entity_ids)
        ).all()
        for comment in comments:
            source_title = None
            if comment.source_type == 'card':
                source_title = comment.source.name
            elif comment.source_type == 'deck':
                snapshot = comment.source.published_snapshot()
                source_title = snapshot.title if snapshot else None
            entity_map[comment.entity_id].update({
                'user': {
                    'badge': comment.user.badge,
                    'username': comment.user.username
                },
                'created': comment.created,
                'text': comment.text,
                'source_title': source_title,
                'source_type': comment.source_type,
                'url': comment.url
            })
    pagination = get_pagination(stream_query.count(), page, per_page)
    return [entity_map[x.Stream.entity_id] for x in stream], page, pagination
