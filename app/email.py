from threading import Thread
from flask import render_template, current_app
from flask_mail import Message


from app import mail


def send_password_reset_email(user, recipients, sender):
    """Send password reset email"""

    token = user.create_password_reset_token()
    send_mail(recipients=recipients, sender=sender,
              html_body=render_template('emails/email_html.html', token=token,
                                        user=user))


def send_mail(recipients, sender, html_body):
    """Send mail using flask mail object's send method"""

    msg = Message(subject='OurChatRoom: Reset Your Password',
                  recipients=recipients, sender=sender)
    msg.html = html_body
    Thread(target=send_async_send, args=(current_app._get_current_object(),
                                         msg)).start()


def send_async_send(app, message):
    """Send mails asynchronously using separate threads"""

    with app.app_context():
        mail.send(message)
