#!/usr/bin/env python3

from application import app
from application.views import index as public_index, player as public_player


app.register_blueprint(public_index.mod)
app.register_blueprint(public_player.mod)
