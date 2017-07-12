from datetime import datetime
import uuid

from application import db


class Invite(db.Model):
    uuid = db.Column(db.String(36), primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    requests = db.Column(db.Integer, nullable=False, default=1)
    requested = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get_for_email(email):
        invitation = Invite.query.filter(Invite.email == email).first()
        if invitation:
            invitation.requests = invitation.requests + 1
        else:
            invitation = Invite(
                uuid=str(uuid.uuid4()),
                email=email
            )
            db.session.add(invitation)
        db.session.commit()
        return invitation
