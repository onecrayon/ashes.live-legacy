from collections import defaultdict

from flask import current_app
from flask_login import current_user

from app import db
from app.models.deck import Deck
from app.models.stream import Stream, Streamable, Subscription, UserStream
from app.utils import get_pagination


def new_entity():
    """Creates a new Streamable entity and returns the ID"""
    entity = Streamable()
    db.session.add(entity)
    db.session.commit()
    return entity.entity_id


def get_stream(page=None):
    """Returns a stream of site entities and pagination information"""
    if not page:
        page = 1
    per_page = current_app.config['DEFAULT_PAGED_RESULTS']
    user_id = current_user.id if current_user else None
    stream_query = db.session.query(
        Stream,
        Subscription.created.label('subscription_start'),
        UserStream.is_delivered
    ).outerjoin(
        Subscription, db.and_(
            Subscription.entity_id == Stream.entity_id,
            Subscription.user_id == user_id
        )
    ).outerjoin(
        UserStream, db.and_(
            UserStream.stream_id == Stream.id,
            UserStream.user_id == user_id
        )
    )
    stream = stream_query.order_by(Stream.posted.desc()).limit(per_page).offset(
        (page - 1) * per_page
    ).all()
    entity_ids = defaultdict(list)
    entity_map = {}
    for entity, subscription_start, is_delivered in stream:
        entity_ids[entity.entity_type].append(entity.entity_id)
        entity_map[entity.entity_id] = {
            'entity_type': entity.entity_type,
            'is_subscribed': subscription_start <= entity.posted if subscription_start else False,
            'is_delivered': is_delivered
        }
    # Gather the latest public snapshots for all decks in the stream
    if 'deck' in entity_ids:
        snapshot_comp = db.aliased(Deck)
        source_comp = db.aliased(Deck)
        decks = db.session.query(Deck, source_comp.entity_id).options(
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
            source_comp.entity_id.in_(entity_ids['deck']),
            snapshot_comp.id.is_(None),
            Deck.is_snapshot.is_(True),
            Deck.is_public.is_(True)
        ).all()
        for deck, entity_id in decks:
            entity_map[entity_id].update({
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
    # TODO: gather comments
    if 'comment' in entity_ids:
        pass
    pagination = get_pagination(stream_query.count(), page, per_page)
    return [entity_map[x.Stream.entity_id] for x in stream], page, pagination
