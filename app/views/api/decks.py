from flask import current_app, Blueprint, jsonify, request

mod = Blueprint('api_decks', __name__, url_prefix='/api/decks')


@mod.route('/')
def listing():
    return jsonify({'error': 'Coming soon'})


@mod.route('/', methods=['POST'])
@mod.route('/<int:deck_id>', methods=['POST'])
def save(deck_id=None):
    # TODO
    data = request.get_json()
    current_app.logger.debug('got data: {}'.format(data))
    return jsonify({'success': 'content received'})
