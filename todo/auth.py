from flask import Blueprint, request, redirect, url_for, flash, session, render_template
import validators
from itsdangerous import URLSafeTimedSerializer as Serializer, SignatureExpired, BadTimeSignature
from todo.emails import create_new_user
from todo.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail


s = Serializer('secret_key')
mail = Mail()

auth = Blueprint('auth', __name__, url_prefix='')



@auth.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        firstName = request.form.get("firstName")
        lastName = request.form.get("lastName")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        
        cur = db.connection.cursor()
        cur.execute("SELECT * from users WHERE email = %s", [email])
        email_exists = cur.fetchone()

        if email_exists:
            flash("Email in use, Please use another.", category='error')
        elif not validators.email(email):
            flash('Invalid email!.', category='error')
        elif password1 != password2:
            flash("Password don't match, Try again!", category='error') 
        elif len(email) < 5:
            flash("Email is too short, Try again!", category='error') 
        elif len(password1) < 6:
            flash("Password is too short, Try again!", category='error')

        else:
            pwd_hash = generate_password_hash(password2, method='sha256')
            cursor = db.connection.cursor()
            user = ("INSERT INTO users"
                    "(email, last_name, first_name, password)"
                    "VALUES(%s, %s, %s, %s)")
            data = (email, lastName, firstName, pwd_hash)
            cursor.execute(user, data)
            db.connection.commit()
            session['loggedin'] = True
            session['name'] = f'{lastName} {firstName}'
            cursor.close()
            token = s.dumps(email, salt=('email-confirm'))
            create_new_user(email, token)
            flash(f"An email has been sent to {email}. Follow the link to verify mail.", category='success')
            return redirect(url_for('auth.verify'))

    return render_template("signup.html")



@auth.route("/confirm_email<token>")
def confirm_email(token):
    try:
        email = s.loads(token, salt="email-confirm", max_age=900)
    except SignatureExpired:
        flash('Token is expired', category='error')
    except BadTimeSignature:
        flash('Token is invalid!', category='error')

    cur = db.connection.cursor()
    cur.execute("SELECT * from users WHERE email = %s", [email])
    user = cur.fetchone()
    if user:
        cur.execute("UPDATE users SET email_verified = true WHERE email = %s", [email])
        db.connection.commit()
        cur.close()
        flash('Email verified!', category='success')
    return render_template('verified.html')