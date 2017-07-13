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
            # Grab a unique UUID
            uuid = str(uuid.uuid4())
            while Invite.get(uuid):
                uuid = str(uuid.uuid4())
            # Create our invitation
            invitation = Invite(
                uuid=uuid,
                email=email
            )
            db.session.add(invitation)
        db.session.commit()
        return invitation
