import os, sys
import secrets
import json, time

from flask import render_template, url_for, flash, redirect, request, abort, make_response
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from Vault.utils.authentication.database.table import User, File, Manager, Directory
from Vault.utils.app import *
from Vault.utils.app.forms import auth
from Vault.utils.cryptographie import hash
from Vault.utils.authentication import Credentials
from Vault.utils.authentication.generator import gen_user_id
from Vault import *

style_bg_status_blue = 'background: rgb(72,146,227);background: radial-gradient(circle, rgba(72,146,227,0.5) 11%, rgba(72,146,227,0.6) 34%, rgba(60,60,60,1) 81%); '
style_bg_status_red = 'background: rgb(227, 72, 72);background: radial-gradient(circle, rgba(227, 72, 72,0.5) 11%, rgba(227, 72, 72,0.6) 34%, rgba(60,60,60,1) 81%);'

@app.before_first_request
def create_tables():
    db.create_all()

@app.route("/", methods=['GET', 'POST'])
def register():
    form = auth()
    if form.validate_on_submit():
        user_manager_id = gen_user_id(form.username_input.data)
        authentication = Credentials(form.username_input.data, form.password_input.data, user_manager_id)
        secret_key = authentication.get_SecretKey()
        salt = secret_key[0:16]
        hashed_master_password = hash(form.password_input.data, 14082, salt)
        hashed_username = hash(form.username_input.data, 14082, salt)
        form.username_input.data = "FUCK U "
        form.password_input.data = "IN THE ASS!"

        if len(User.query.filter_by(user_manager_id=user_manager_id).all()) == 0:
            user = User(username=hashed_username, master_password=hashed_master_password, user_manager_id=user_manager_id)
            db.session.add(user)
            db.session.commit()
            login_user(user)

            session_name = hashed_username + current_user.get_id()
            session[session_name+"iv"] = secret_key[16:]
            session[session_name+"salt"] = secret_key[0:16]

            del hashed_username
            del hashed_master_password
            del user

            return render_template('register.html', form=form, style_bg_status=style_bg_status_blue)
        else:
            return render_template('register.html', form=form, style_bg_status=style_bg_status_red)
    return render_template('register.html', form=form, style_bg_status=style_bg_status_blue)