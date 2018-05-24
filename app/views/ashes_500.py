"""Ashes 500 card listing"""

from flask import abort, Blueprint, render_template

from app import db
from app.models.ashes_500 import Ashes500Revision

mod = Blueprint('ashes_500', __name__, url_prefix='/ashes-500')


@mod.route('/')
def index():
    revision = Ashes500Revision.query.order_by(Ashes500Revision.id.desc()).first()
    if not revision:
        abort(404)
    return render_template(
        'ashes_500/index.html',
        revision=revision
    )
