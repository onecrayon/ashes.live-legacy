from application import db


card_dice = db.Table(
    'cards_dice',
    db.Column('card_id', db.Integer, db.ForeignKey('card.id')),
    db.Column('die_id', db.Integer, db.ForeignKey('die.id'))
)


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(25), nullable=False, index=True, unique=True)
    stub = db.Column(db.String(25), nullable=False, index=True, unique=True)
    release = db.Column(db.Integer, nullable=False, index=True, default=0)
    card_type = db.Column(db.String(25), nullable=False, index=True)
    cost_weight = db.Column(db.Integer, nullable=False, index=True, default=0)
    json = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text, nullable=False)
    
    dice = db.relationship('Die', secondary=card_dice, back_populates='cards')


class Die(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(10))
    
    cards = db.relationship('Card', secondary=card_dice, back_populates='dice')
