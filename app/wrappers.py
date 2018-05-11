from functools import wraps

from flask import abort, redirect, url_for
from flask_login import current_user, fresh_login_required


def guest_required(function):
	@wraps(function)
	def decorated_function(*args, **kwargs):
		if current_user.is_authenticated:
			return redirect(url_for('home.index'))
		return function(*args, **kwargs)
	return decorated_function


def admin_required(function):
	@fresh_login_required
	@wraps(function)
	def decorated_function(*args, **kwargs):
		if not current_user.is_admin:
			return abort(404)
		return function(*args, **kwargs)
	return decorated_function
