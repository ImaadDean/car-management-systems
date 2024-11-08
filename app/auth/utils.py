from flask import url_for
from flask_mail import Message
from app import mail
from itsdangerous import URLSafeTimedSerializer
from config import Config

serializer = URLSafeTimedSerializer(Config.SECRET_KEY)

def send_confirmation_email(user_email):
    token = serializer.dumps(user_email, salt='email-confirm')
    msg = Message('Confirm Your Email', recipients=[user_email])
    link = url_for('auth.confirm_email', token=token, _external=True)
    msg.body = f'Click the following link to confirm your email: {link}'
    mail.send(msg)