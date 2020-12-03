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
    class controller(FlaskForm):
        search_input = StringField('')
    class add(FlaskForm):
        folder_name_input = StringField("Folder name")
        folder_tag_input = StringField('')
        submit = SubmitField('Create')
    class vault_add(FlaskForm):
        vault_name = StringField("Vault name")
        vault_username = StringField("Vault username")
        vault_password = StringField("Vault password")
        vault_password_generate = SubmitField('generate')
        vault_tag = StringField('')
        submit = SubmitField('Create')
class credit_card(FlaskForm):
    password = StringField("Vault password")
    generate = SubmitField('Yes')
    submit = SubmitField('Create')