from app import db
from app.models.post import Post


def get_pinned_posts(section_id=None):
    query = db.session.query(Post).options(
        db.joinedload('user'),
        db.joinedload('section')
    ).filter(
        Post.is_pinned.is_(True),
        Post.is_deleted.is_(False)
    )
    if section_id:
        query = query.filter(
            Post.section_id == section_id
        )
    return query.order_by(Post.created.desc()).all()
