from app.models.card import Card, Die


def global_json():
    cards = Card.query.all()
    dice = Die.query.all()
    cards_json = ''.join(['[', ','.join([x.json for x in cards]), ']'])
    dice_json = ''.join(['[\'', '\',\''.join([x.stub for x in dice]), '\']'])
    return {'cards_json': cards_json, 'dice_json': dice_json}
