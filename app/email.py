from threading import Thread
from flask import url_for
from flask_mail import Message


from app import app, mail


def send_password_reset_email(user, recipients, sender):
    """Send password reset email"""

    token = user.create_password_reset_token()
    send_mail(recipients=recipients, sender=sender, token=token)


def send_mail(recipients, sender, token):
    """Send mail using flask mail object's send method"""

    msg = Message(subject='Microblog: Reset Your Password',
                  recipients=recipients, sender=sender)
    msg.html = "<a href='https://reset_password_request/{{ token }}'>Reset</a>"
    Thread(target=send_async_send, args=(app, msg)).start()


def send_async_send(app, message):
    """Send mails asynchronously using separate threads"""

    with app.app_context():
        mail.send(message)
