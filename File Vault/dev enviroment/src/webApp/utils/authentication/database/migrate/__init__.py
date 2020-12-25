from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from datetime import timedelta
from flask import Flask, session
#from flask_session import Session

import secrets, os
import mimetypes

app = Flask(__name__)
app.config.update(dict(
    SECRET_KEY = secrets.token_hex(),
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database_migrated.db',
    SQLALCHEMY_TRACK_MODIFICATIONS = False,
    SESSION_TYPE = 'filesystem',    
))
app.permanent_session_lifetime = timedelta(minutes=5)
db = SQLAlchemy(app)