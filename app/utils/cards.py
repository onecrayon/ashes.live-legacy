import json

from app.models.ashes_500 import Ashes500Value
from app.models.card import Card


def global_json(ashes_500_revision_id=None):
    cards = Card.query.all()
    cards_json = ''.join(['[', ','.join([x.json for x in cards]), ']'])
    if ashes_500_revision_id:
        ashes_500_values = Ashes500Value.query.filter(
            Ashes500Value.revision_id == ashes_500_revision_id
        ).all()
        return {
            'cards_json': cards_json,
            'ashes_500_json': json.dumps([{
                'card_id': x.card_id,
                'combo_card_id': x.combo_card_id,
                'qty_1': x.qty_1,
                'qty_2': x.qty_2,
                'qty_3': x.qty_3
            } for x in ashes_500_values])
        }
    return {'cards_json': cards_json}
