"""Comment editing and moderation"""

from flask import abort, Blueprint, redirect, render_template
from flask_login import login_required

from app import db

mod = Blueprint('comments', __name__, url_prefix='/comments')


@mod.route('/<int:comment_id>/', methods=['GET', 'POST'])
def edit(comment_id):
	pass


@mod.route('/<int:comment_id>/delete/')
def delete(comment_id):
	pass


@mod.route('/<int:comment_id>/moderate/', methods=['GET', 'POST'])
def moderate(comment_id):
	pass
