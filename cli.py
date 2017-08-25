#!/usr/bin/env python3
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app import db
from app.models import (
    card, deck, invite, user
)
from manager import app

# Grab access to the session model, so that Alembic can see its table definition
session_model = app.session_interface.sql_session_model

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
