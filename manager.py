#!/usr/bin/env python3

from application import app
from application.views import index as public_index


app.register_blueprint(public_index.mod)
