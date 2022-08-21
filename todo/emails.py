from flask import url_for
from flask_mail import Message, Mail

mail = Mail()

def create_new_user(email, token, name):
    msg = Message('Confirm Email.', sender='Yusuf S.A.', recipients=[email])

    msg.body = f"""
Hello {name},
    You just took the first step to freedom. 
    Follow the link below to verify your mail.

                                Yours truly.
                                Yusuf S.A.

{url_for('auth.confirm_email', token=token, _external=True)}

If you did not make this request then simply ignore this mail.
    """
    mail.send(msg)