from flask import current_app, render_template
from flask_mail import Message
from premailer import transform as inline_css

from app import mail


def send_message(recipient, subject, template_name, sender=None, **kwargs):
    """Sends a two-part HTML+text email using the following files:
    
    * templates/emails/{template_name}.html
    * templates/emails/{template_name}.txt
    
    Any keyword arguments are passed straight through to the templates.
    
    All templates autmatically receive the following keyword arguments:
    
    * {{ subject }}: the email subject (used as a title for the base template)
    * {{ site_url }}: the site root URL
    """
    message = Message(
        subject,
        recipients=[recipient],
        sender=sender if sender else current_app.config['MAIL_DEFAULT_SENDER'],
        html=inline_css(render_template(
            'emails/{}.html'.format(template_name),
            subject=subject,
            site_url=current_app.config['SITE_URL'],
            cdn_url=current_app.config['CDN_URL'] if current_app.config['CDN_URL']
                else current_app.config['SITE_URL'],
            **kwargs
        )),
        body=render_template(
            'emails/{}.txt'.format(template_name),
            subject=subject,
            site_url=current_app.config['SITE_URL'],
            **kwargs
        )
    )
    mail.send(message)
