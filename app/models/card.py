from enum import Enum

from sqlalchemy_fulltext import FullText

from app import db


class DiceFlags(Enum):
    basic = 0
    ceremonial = 1
    charm = 2
    illusion = 4
    natural = 8
    divine = 16
    sympathy = 32


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(25), nullable=False, index=True, unique=True)
    stub = db.Column(db.String(25), nullable=False, index=True, unique=True)
    phoenixborn = db.Column(db.String(25), nullable=True, index=True)
    release = db.Column(db.Integer, nullable=False, index=True, default=0)
    card_type = db.Column(db.String(25), nullable=False, index=True)
    is_summon_spell = db.Column(db.Boolean, nullable=False, default=False)
    cost_weight = db.Column(db.Integer, nullable=False, index=True, default=0)
    dice_flags = db.Column(db.Integer, nullable=False, index=True, default=0)
    split_dice_flags = db.Column(db.Integer, nullable=False, index=True, default=0)
    copies = db.Column(db.SmallInteger, nullable=True, default=None)
    json = db.Column(db.Text)
    text = db.Column(db.Text)
    summon_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=True)
    
    conjurations = db.relationship('Card')

    @staticmethod
    def dice_to_flags(dice_list):
        flags = 0
        if not dice_list:
            return flags
        for die in dice_list:
            flags = flags | DiceFlags[die].value
        return flags

    @staticmethod
    def flags_to_dice(flags_int):
        dice = [die.name for die in DiceFlags if die.value & flags_int == die.value]
        return dice if dice else None

    @staticmethod
    def has_any_dice_filter(dice):
        if not dice:
            dice = ['basic']
        return db.or_(
            *[Card.dice_flags.op('&')(DiceFlags[die].value) == DiceFlags[die].value for die in dice]
        )
    
    @staticmethod
    def has_all_dice_filter(dice):
        flags = Card.dice_to_flags(dice)
        return db.and_(
            Card.dice_flags.op('&')(flags) == flags
        )


class NameTextSearch(FullText, Card):
    __fulltext_columns__ = ('name', 'text')


# Define our index to ensure Alembic can automatically generate future migrations
db.Index('ix_card_text', Card.name, Card.text)
