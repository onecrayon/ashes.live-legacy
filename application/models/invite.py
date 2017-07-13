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
            str_id = str(uuid.uuid4())
            while Invite.query.get(str_id):
                str_id = str(uuid.uuid4())
            # Create our invitation
            invitation = Invite(
                uuid=str_id,
                email=email
            )
            db.session.add(invitation)
        db.session.commit()
        return invitation
