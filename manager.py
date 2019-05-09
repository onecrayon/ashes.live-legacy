#!/usr/bin/env python3

from app import app, error_handlers
from app.views import (
   ashes_500 as public_ashes_500, cards as public_cards, comments as public_comments,
   decks as public_decks, home as public_home, phoenix as public_phoenix, player as public_player,
   posts as public_posts, api
)
from app.views.api import (
    cards as api_cards, decks as api_decks
)


app.register_blueprint(api.mod)
app.register_blueprint(api_cards.mod)
app.register_blueprint(api_decks.mod)
app.register_blueprint(error_handlers.mod)
app.register_blueprint(public_ashes_500.mod)
app.register_blueprint(public_cards.mod)
app.register_blueprint(public_comments.mod)
app.register_blueprint(public_decks.mod)
app.register_blueprint(public_home.mod)
app.register_blueprint(public_phoenix.mod)
app.register_blueprint(public_player.mod)
app.register_blueprint(public_posts.mod)
