#Note to start this on the 20th of august
#Note to end it by 10th of september


import os 
from flask import Flask 
from flask import Flask, render_template
from flask_login import LoginManager
from flask_mail import Mail
from os import path
from todo.auth import auth
from todo.routes import routes
from todo.extensions import db



def create_app(test_config=None):
    app = Flask(__name__)
    if test_config is None:
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
        app.config['MYSQL_HOST'] = 'localhost'
        app.config['MYSQL_USER'] = 'root'
        app.config['MYSQL_PASSWORD'] = 'password'
        app.config['MYSQL_DB'] = 'todo db here'
        app.config['MYSQL_CONNECT_TIMEOUT'] = 360
        app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['MAIL_SERVER']='smtp.gmail.com'
        app.config['MAIL_PORT'] = 465
        app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
        app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
        app.config['MAIL_USE_TLS'] = False
        app.config['MAIL_USE_SSL'] = True
    else:
        app.config.from_mapping(test_config)

    db.init_app(app)

    app.register_blueprint(auth)
    app.register_blueprint(routes)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.signin'
    login_manager.init_app(app)

    mail = Mail()
    mail.init_app(app)

    @login_manager.user_loader
    def load_user(id):    
        cur = db.connection.cursor()
        cur.execute("SELECT * from users WHERE user_id = %d", [id])
        return cur.fetchone()
        
    @app.errorhandler(404) 
    def error_404(e): 
        return render_template("404.html"), 404
  
    @app.errorhandler(500) 
    def error_500(e): 
        return render_template("500.html"), 500

    return app
