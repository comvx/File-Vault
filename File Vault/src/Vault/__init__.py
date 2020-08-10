from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from datetime import timedelta
from flask import Flask, session
from flask_session import Session

import secrets, os

app = Flask(__name__)
app.config.update(dict(
    SECRET_KEY = secrets.token_hex(),
    SQLALCHEMY_DATABASE_URI = 'sqlite:///utils/authentication/database/database.db',
    SQLALCHEMY_TRACK_MODIFICATIONS = False,
    SESSION_TYPE = 'filesystem',    
))
app.permanent_session_lifetime = timedelta(minutes=5)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.session_protection = "strong"
Session(app)

from Vault.utils.app import *
