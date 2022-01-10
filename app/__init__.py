from os.path import join, dirname, realpath
import os
from flask_login import  login_required, LoginManager, UserMixin, login_manager, login_user, current_user, logout_user
from flask import Flask, request, session, render_template, url_for, flash, get_flashed_messages, message_flashed
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import PY3, Bcrypt
from sqlalchemy.orm import relationship
from flask_wtf import Form
from wtforms import StringField, PasswordField, validators
from werkzeug.utils import redirect, secure_filename
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import EmailField, SubmitField, FileField

from flask import Flask, abort
from flask import render_template, request
from flask.helpers import flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_manager, LoginManager, current_user, login_required, login_user, logout_user, UserMixin, user_logged_in
from werkzeug.utils import redirect

# app creation adn configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Lethabo2016.@localhost:3306/app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"
db = SQLAlchemy(app)


# handling logins







app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Lethabo2016.@localhost:3306/app'

# Secret Key!
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Initialize The Database
db = SQLAlchemy(app)
with app.app_context():
    db.create_all()



UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/uploads/..')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Login to Continue"



def GetApp():
    return app

if __name__ =="__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

from app import routes