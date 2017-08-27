#!/usr/bin/env python3

from app import app, error_handlers
from app.views import (
	decks as public_decks, home as public_home, player as public_player,
	api
)
from app.views.api import (
	cards as api_cards, decks as api_decks
)


app.register_blueprint(api.mod)
app.register_blueprint(api_cards.mod)
app.register_blueprint(api_decks.mod)
app.register_blueprint(error_handlers.mod)
app.register_blueprint(public_decks.mod)
app.register_blueprint(public_home.mod)
app.register_blueprint(public_player.mod)
