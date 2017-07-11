from urllib.parse import urljoin, urlparse

from flask import redirect, request, url_for
from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, PasswordField, StringField
from wtforms.validators import Email


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def get_redirect_target():
    return request.args.get('next') if is_safe_url(request.args.get('next')) else None


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        Email(message='You must enter an email address.')
    ])
    password = PasswordField('Password')
    remember_me = BooleanField('Remember me')
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = get_redirect_target() or ''

    def redirect(self, endpoint='index.landing_page', **values):
        if is_safe_url(self.next.data):
            return redirect(self.next.data)
        return redirect(url_for(endpoint, **values))
