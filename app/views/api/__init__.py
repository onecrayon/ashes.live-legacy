from flask import Blueprint, jsonify

mod = Blueprint('api', __name__, url_prefix='/api')


@mod.route('/')
def api_version():
    return jsonify({
        'version': 'v1',
        'description': (
            'The Ashes.live API offers RESTful access to card data for '
            'Ashes: Rise of the Phoenixborn by Plaid Hat Games. Please '
            'use responsibly so I can continue to offer it. :-)'
        )
    })
