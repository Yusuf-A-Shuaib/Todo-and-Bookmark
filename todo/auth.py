from flask import Blueprint, request, redirect, url_for, flash, session, render_template
import validators
import os
from itsdangerous import URLSafeTimedSerializer as Serializer, SignatureExpired, BadTimeSignature
from todo.emails import create_new_user, login_on_account
from todo.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail


s = Serializer(os.environ.get('SECRET_KEY'))
mail = Mail()

auth = Blueprint('auth', __name__, url_prefix='auth')



@auth.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        fullname = request.form.get("fullname")
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
                    "(email, fullname, password)"
                    "VALUES(%s, %s, %s)")
            data = (email, fullname, pwd_hash)
            cursor.execute(user, data)
            db.connection.commit()
            session = True
            session['name'] = f'{fullname}'
            cursor.close()
            token = s.dumps(email, salt=('email-confirm'))
            create_new_user(email, token, fullname)
            flash(f"An email has been sent to {email}. Follow the link to verify mail.", category='success')
            return redirect(url_for('auth.login'))
    return render_template("signup.html")


@auth.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        password = request.form.get("password")
        if not validators.email(email):
            flash('Invalid email syntax', category='error')

        cur = db.connection.cursor()
        cur.execute("SELECT * from users WHERE email = %s OR fullname = %s", [email, fullname])
        email_exists = cur.fetchone()
        if email_exists:
            if check_password_hash(email_exists['password'], password):
                session['name'] = email_exists['last_name']
                session['loggedin'] = True
                login_on_account(email)
                return redirect(url_for('views.home', id=email_exists['user_id']))
            else:
                flash("Password is incorrect, Try again!", category='error')
        else:
            flash("Email does not exist, Try again!", category='error')
    
    return render_template("login.html")


@auth.route('/requestverifymail-token/<email>')
def request_verify_mail_token(email):
    cur = db.connection.cursor()
    cur.execute("SELECT * from users WHERE email = %s", [email])
    email_exists = cur.fetchone()
    if email_exists:
        token = s.dumps(email, salt=('email-confirm'))
        create_new_user(email, token, email_exists['lastname'])
    return redirect(url_for('routes.home'))

@auth.route("/confirm_email<token>")
def confirm_email(token):
    try:
        email = s.loads(token, salt="email-confirm", max_age=900)
    except SignatureExpired:
        flash('Token is expired', category='error')
        return redirect(url_for('auth.request_verify_mail_token', email=email))
    except BadTimeSignature:
        flash('Token is invalid!', category='error')
        return redirect(url_for('auth.request_verify_mail_token', email=email))

    cur = db.connection.cursor()
    cur.execute("SELECT * from users WHERE email = %s", [email])
    user = cur.fetchone()
    if user:
        cur.execute("UPDATE users SET email_verified = true WHERE email = %s", [email])
        db.connection.commit()
        cur.close()
        flash('Email verified!', category='success')
    return render_template('verified.html')