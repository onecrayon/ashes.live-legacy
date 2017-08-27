from flask import Blueprint, jsonify

mod = Blueprint('api_cards', __name__, url_prefix='/api/cards')


@mod.route('/')
def listing():
	return jsonify({'error': 'Coming soon'})
