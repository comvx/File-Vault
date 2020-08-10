from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, Label, FileField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError

class auth(FlaskForm):
    username_input = StringField('Email')
    password_input = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('auth')
