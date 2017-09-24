from app.models.card import Card


def global_json():
    cards = Card.query.all()
    cards_json = ''.join(['[', ','.join([x.json for x in cards]), ']'])
    return {'cards_json': cards_json}
