from app import db
from app.views.forms.comment import CommentForm

def get_comments(entity_id, source_type='deck', page=None):
    # TODO: gather actual comments
    comments = []
    comment_form = CommentForm(source_entity_id=entity_id, source_type=source_type)
    return comments, comment_form
