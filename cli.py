#!/usr/bin/env python3
import fileinput

from flask import current_app
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app import db
from app.models import (
   ashes_500, card, comment, deck, invite, phoenix_dice, post, release, stream, user
)
from manager import app

# Grab access to the session model, so that Alembic can see its table definition
session_model = app.session_interface.sql_session_model

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def cdnize_style_urls():
    """Converts relative URLs in production CSS file into CDN URLs"""
    with fileinput.FileInput('./app/static/css/styles.min.css', inplace=True) as file:
        for line in file:
            # Within fileinputs stdout is redirected into the file
            print(line.replace('url(../images', 'url({}/images'.format(
                current_app.config['CDN_URL']
            )), end='')


@manager.command
def local_dev():
    """Toggles all automated emails off for local development"""
    db.session.query(user.User).filter(db.or_(
        user.User.email_subscriptions.is_(True)
    )).update({'email_subscriptions': False, 'newsletter_opt_in': True})
    db.session.commit()
    print('Site emails disabled!')


if __name__ == '__main__':
    manager.run()
