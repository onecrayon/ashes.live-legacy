from app import db
from app.models.user import User


class Subscription(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True, nullable=False)
    # This pairs the subscribed content's ID and table name; e.g. 'card' or 'deck'
    subscribed_id = db.Column(db.Integer, primary_key=True, nullable=False)
    subscribed_type = db.Column(db.String(16), primary_key=True, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subscribed_id = db.Column(db.Integer, nullable=False)
    subscribed_type = db.Column(db.String(16), nullable=False)
    # The source is the content that caused the notification; e.g. a comment
    source_id = db.Column(db.Integer, nullable=False)
    source_type = db.Column(db.String(16), nullable=False)
    title = db.Column(db.String(255))
    markup = db.Column(db.Text)
    plain_text = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class NotificationUser(db.Model):
    notification_id = db.Column(db.Integer, db.ForeignKey(Notification.id), primary_key=True,
                                nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True, nullable=False)
    is_delivered = db.Column(db.Boolean, default=False, nullable=False)
