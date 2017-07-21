from functools import wraps

from flask import redirect, url_for
from flask_login import current_user


def guest_required(function):
	@wraps(function)
	def decorated_function(*args, **kwargs):
		if current_user.is_authenticated:
			return redirect(url_for('home.index'))
		return function(*args, **kwargs)
	return decorated_function
