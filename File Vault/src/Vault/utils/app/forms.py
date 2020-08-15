from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, Label, FileField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError

class auth(FlaskForm):
    username_input = StringField('Username', validators=[DataRequired()])
    password_input = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('auth')
class data_upload(FlaskForm):
    data = FileField("inputFile", validators=[DataRequired()])
    submit = SubmitField('Upload')
class home_form():
    class add(FlaskForm):
        folder_name_input = StringField("Folder name", validators=[DataRequired()])
        submit = SubmitField('Create')