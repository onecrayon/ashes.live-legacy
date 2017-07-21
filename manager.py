#!/usr/bin/env python3

from app import app, error_handlers
from app.views import (
	decks as public_decks, home as public_home, player as public_player
)


app.register_blueprint(error_handlers.mod)
app.register_blueprint(public_decks.mod)
app.register_blueprint(public_home.mod)
app.register_blueprint(public_player.mod)
