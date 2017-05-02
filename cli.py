#!/usr/bin/env python3
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from application import db
from manager import app

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
