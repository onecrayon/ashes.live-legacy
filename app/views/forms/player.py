from urllib.parse import urljoin, urlparse

from flask import redirect, request, url_for
from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, PasswordField, RadioField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def get_redirect_target():
    return request.args.get('next') if is_safe_url(request.args.get('next')) else None


def strip_filter(value):
    if isinstance(value, str):
        return value.strip()
    return value


# Shared fields
emailField = StringField('Email', validators=[
    Email(message='Invalid email.')
], filters=(strip_filter,))
usernameField = StringField('Username', validators=[DataRequired()])
passwordField = PasswordField('Password', validators=[
    DataRequired(message='Password is required.')
])
passwordConfirmField = PasswordField('Confirm Password', validators=[
    DataRequired(message='Password confirmation is required.'),
    EqualTo('password', message='Must match password.')
])
newsletterField = BooleanField('Notify me of new site features')


class RedirectForm(FlaskForm):
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = get_redirect_target() or ''

    def redirect(self, endpoint='home.index', **values):
        if is_safe_url(self.next.data):
            return redirect(self.next.data)
        return redirect(url_for(endpoint, **values))


class LoginForm(RedirectForm):
    email = emailField
    password = passwordField
    remember_me = BooleanField('Remember me')


class ReauthorizeForm(RedirectForm):
    password = passwordField


class EmailForm(FlaskForm):
    email = emailField


class ResetForm(FlaskForm):
    password = passwordField
    password_confirm = passwordConfirmField


class EditForm(FlaskForm):
    email = StringField('Email', render_kw={'readonly': True})
    username = usernameField
    password = PasswordField('New Password (or leave blank)')
    password_confirm = PasswordField('Confirm Password', validators=[
        EqualTo('password', message='Must match password.')
    ])
    description = TextAreaField('Description')
    newsletter_opt_in = newsletterField


class CreateForm(EditForm):
    badge = RadioField('Badge', validators=[DataRequired()])
    password = passwordField
    password_confirm = passwordConfirmField
