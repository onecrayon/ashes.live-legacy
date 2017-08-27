from flask import Blueprint, jsonify

mod = Blueprint('api_decks', __name__, url_prefix='/api/decks')


@mod.route('/')
def listing():
	return jsonify({'error': 'Coming soon'})
