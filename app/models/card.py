from app import db


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
    is_summon_spell = db.Column(db.Boolean, nullable=False, default=False)
    cost_weight = db.Column(db.Integer, nullable=False, index=True, default=0)
    json = db.Column(db.Text)
    text = db.Column(db.Text)
    summon_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=True)
    
    dice = db.relationship('Die', secondary=card_dice, back_populates='cards')
    conjurations = db.relationship('Card')


class Die(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stub = db.Column(db.String(10), nullable=False, unique=True)
    
    cards = db.relationship('Card', secondary=card_dice, back_populates='dice')


# Define our index to ensure Alembic can automatically generate future migrations
db.Index('ix_card_text', Card.name, Card.text)
