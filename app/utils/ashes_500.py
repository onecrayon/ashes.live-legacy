from collections import defaultdict

from app import db
from app.models.ashes_500 import Ashes500Revision, Ashes500Value


def get_ashes_500_maps(revision_id, ids=None):
    query = Ashes500Value.query.filter(
        Ashes500Value.revision_id == revision_id
    )
    if ids:
        query = query.filter(
            Ashes500Value.card_id.in_(ids)
        )
    ashes_500_values = query.all()
    ashes_500_map = defaultdict(list)
    ashes_500_combo_map = defaultdict(list)
    for values in ashes_500_values:
        ashes_500_map[values.card_id].append({
            'combo_card_id': values.combo_card_id,
            'qty_1': values.qty_1,
            'qty_2': values.qty_2,
            'qty_3': values.qty_3
        })
        if values.combo_card_id:
            ashes_500_combo_map[values.combo_card_id].append(values.card_id)
    return ashes_500_map, ashes_500_combo_map


def latest_ashes_500_revision():
    return db.session.query(Ashes500Revision.id).order_by(
        Ashes500Revision.id.desc()
    ).limit(1).scalar()
