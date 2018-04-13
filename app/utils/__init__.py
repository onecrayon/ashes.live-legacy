import math

from flask import current_app, render_template
from flask_mail import Message
from premailer import transform as inline_css
from sendgrid import SendGridAPIClient
import sendgrid.helpers.mail as sendgrid_helpers

from app import mail


def get_pagination(results_count, page, per_page, spread=2):
    """Returns a list of page numbers for rendering pagination, or None"""
    total_pages = math.ceil(results_count / per_page)
    if total_pages <= 1:
        return None
    pagination = list(range(1, total_pages + 1))
    extra_right = spread - page + 1 if page - 1 < spread else 0
    extra_left = page + spread - total_pages if page + spread > total_pages else 0
    if page + spread + extra_right < total_pages - spread:
        del pagination[page + spread + extra_right:total_pages - 1]
    if page - spread - extra_left > spread + 1:
        del pagination[1:page - spread - extra_left - 1]
    return pagination


def send_message(recipient, subject, template_name, sender=None, **kwargs):
    """Sends a two-part HTML+text email using the following files:
    
    * templates/emails/{template_name}.html
    * templates/emails/{template_name}.txt
    
    Any keyword arguments are passed straight through to the templates.
    
    All templates autmatically receive the following keyword arguments:
    
    * {{ subject }}: the email subject (used as a title for the base template)
    * {{ site_url }}: the site root URL
    """
    html_body = inline_css(render_template(
        'emails/{}.html'.format(template_name),
        subject=subject,
        site_url=current_app.config['SITE_URL'],
        cdn_url=current_app.config['CDN_URL'] if current_app.config['CDN_URL']
            else current_app.config['SITE_URL'],
        **kwargs
    ))
    text_body = render_template(
        'emails/{}.txt'.format(template_name),
        subject=subject,
        site_url=current_app.config['SITE_URL'],
        **kwargs
    )
    if not sender:
        sender = current_app.config['MAIL_DEFAULT_SENDER']

    api_key = current_app.config['SENDGRID_API_KEY']
    response = None
    if api_key:
        api = SendGridAPIClient(apikey=api_key)
        # sender might be a tuple of (name, email)
        from_email = (
            sendgrid_helpers.Email(sender) if isinstance(sender, str)
            else sendgrid_helpers.Email(email=sender[1], name=sender[0])
        )
        to_email = sendgrid_helpers.Email(recipient)
        html_content = sendgrid_helpers.Content('text/html', html_body)
        text_content = sendgrid_helpers.Content('text/plain', text_body)
        # The Mail helper will not actually save anything unless every single attribute is specified
        email = sendgrid_helpers.Mail(
            subject=subject, from_email=from_email, to_email=to_email, content=text_content
        )
        email.add_content(html_content)
        email_data = email.get()
        try:
            response = api.client.mail.send.post(request_body=email_data)
            if response.status_code >= 400:
                current_app.logger.error('Mail delivery failed ({}): {}'.format(
                    response.status_code, response.body
                ))
        except Exception as e:
            current_app.logger.error('Failed to send email via SendGrid API: {}'.format(e.body))
            current_app.logger.error('Mail request body: {}'.format(email_data))

    # Exit if we successfully sent our email via SendGrid; otherwise try sending via SMTP
    if response and response.status_code < 400:
        return

    message = Message(
        subject,
        recipients=[recipient],
        sender=sender,
        html=html_body,
        body=text_body
    )
    mail.send(message)
