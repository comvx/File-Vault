import os, sys
import secrets
import json, time

from flask import render_template, url_for, flash, redirect, request, abort, make_response
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from werkzeug.utils import secure_filename

from Vault.utils.authentication.database.table import User, File, Directory
from Vault.utils.app import *
from Vault.utils.app.forms import auth, data_upload, home_form
from Vault.utils.cryptographie import hash
from Vault.utils.authentication import Credentials
from Vault.utils.authentication.generator import gen_user_id
from Vault.utils.data import *
from Vault import *

style_bg_status_blue = 'background: rgb(72,146,227);background: radial-gradient(circle, rgba(72,146,227,0.5) 11%, rgba(72,146,227,0.6) 34%, rgba(60,60,60,1) 81%); '
style_bg_status_red = 'background: rgb(227, 72, 72);background: radial-gradient(circle, rgba(227, 72, 72,0.5) 11%, rgba(227, 72, 72,0.6) 34%, rgba(60,60,60,1) 81%);'


@app.before_first_request
def create_tables():
    db.create_all()

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect("/home?path=")
    else:
        return redirect(url_for('login'))

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect("/")
    form = auth()
    if form.validate_on_submit():
        user_manager_id = gen_user_id(form.username_input.data)
        authentication = Credentials(form.username_input.data, form.password_input.data, user_manager_id)
        secret_key = authentication.get_SecretKey()
        salt = secret_key[0:16]
        hashed_master_password = hash(form.password_input.data, 14082, salt)
        hashed_username = hash(form.username_input.data, 14082, salt)
        form.username_input.data = ""
        form.password_input.data = ""

        if len(User.query.filter_by(user_manager_id=user_manager_id).all()) == 0:
            user = User(username=hashed_username, master_password=hashed_master_password, user_manager_id=user_manager_id)
            db.session.add(user)
            db.session.commit()
            login_user(user)

            root_dir = Directory(dir_name="root", dir_path="/root", user=current_user)
            db.session.add(root_dir)
            test = File(file_name="test", file_ext="txt", file_data="test")
            root_dir.files.append(test)
            root_dir = Directory(dir_name="folder_1", dir_path="/root/folder_1", user=current_user)
            db.session.add(root_dir)
            test = File(file_name="test_1", file_ext="db", file_data="db_data")
            root_dir.files.append(test)
            db.session.commit()

            session_name = hashed_username + current_user.get_id()
            session[session_name+"iv"] = secret_key[16:]
            session[session_name+"salt"] = secret_key[0:16]

            del hashed_username
            del hashed_master_password
            del user

            return redirect(url_for('index'))
        else:
            return render_template('register.html', form=form, style_bg_status=style_bg_status_red)
    return render_template('register.html', form=form, style_bg_status=style_bg_status_blue)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/")
    form = auth()
    if form.validate_on_submit():
        try:
            user_manager_id = gen_user_id(form.username_input.data)
            authentication = Credentials(form.username_input.data, form.password_input.data, user_manager_id)
            secret_key = authentication.get_SecretKey()
            salt = secret_key[0:16]
            hashed_master_password = hash(form.password_input.data, 14082, salt)
            hashed_username = hash(form.username_input.data, 14082, salt)
            form.username_input.data = ""
            form.password_input.data = ""

            user = User.query.filter_by(user_manager_id=user_manager_id, username=hashed_username, master_password=hashed_master_password).first()
            if user:
                login_user(user, remember=True)

                session_name = hashed_username + current_user.get_id()
                session[session_name+"iv"] = secret_key[16:]
                session[session_name+"salt"] = secret_key[0:16]

                del hashed_username
                del hashed_master_password
                del user

                time.sleep(2.2)
                return redirect(url_for('index'))
            else:
                time.sleep(2.2)
                return render_template('login.html', form=form, style_bg_status=style_bg_status_red, message="Wrong username and/or password")
        except Exception as identifier:
            time.sleep(2.2)
            return render_template('login.html', form=form, style_bg_status=style_bg_status_red, message="Wrong username and/or password")
    return render_template('login.html', form=form, style_bg_status=style_bg_status_blue)

def transform_dataset(ppath):
    absolute_path = ppath
    ppath = ppath.split("/")[-1]
    dirs = current_user.directorys

    output = list()
    for directory in dirs:
        focused_dir = directory.dir_path.split("/")[-1]
        if str(focused_dir) == str(ppath):
            for file in directory.files:
                data_set = dataset(file.file_name, file.file_ext, directory.dir_path, file.file_data, directory.dir_path+"/"+file.file_name+"."+file.file_ext)
                output.append(data_set.data_set)
        if directory.dir_path.count("/") > absolute_path.count("/"):
            child_dir = directory.dir_path.replace(absolute_path, "")
            if len(child_dir.split("/")) == 2:
                data_set = dataset(directory.dir_name, "folder", directory.dir_path, "", directory.dir_path)
                output.append(data_set.data_set)

    return output

def check_for_twice_name(path, name):
    dirs = current_user.directorys
    for directory in dirs:
        if str(directory.dir_path) == str(path+"/"+name):
            return False
    return True

def duplicates(folder_name, current_path):
    dirs = current_user.directorys
    new_path = current_path+"/"+folder_name
    for directory in dirs:
        if str(directory.dir_path) == str(new_path):
            return False
    return True

@app.route("/home", methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated:
        calling_path = request.args.get('path')
        home = home_form()
        home_add = home.add()
        current_folder_path = ""

        if home_add.validate_on_submit():
            if home_add.submit:
                if duplicates(home_add.folder_name_input.data, calling_path):
                    new_dir = Directory(dir_name=home_add.folder_name_input.data, dir_path=calling_path+"/"+home_add.folder_name_input.data, user=current_user)
                    db.session.add(new_dir)
                    db.session.commit()

        dataset = transform_dataset(calling_path)

        calling_path_splitter = calling_path.split("/")

        return render_template('home.html', data_set=dataset, home_add=home_add, current_folder_path=calling_path+"/", current_folders=calling_path_splitter, current_folder_href=calling_path)
    else:
        return redirect(url_for("login"))

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    form = data_upload()
    if form.validate_on_submit():
        files = request.files.getlist(form.data.name)
        if files:
            for file in files:
                file_contents = file.stream.read()
                file_name = secure_filename(file.filename)
            time.sleep(5)
    return render_template("upload.html", form=form)

def delete_childs(absolute_path):
    dirs = current_user.directorys
    for directory in dirs:
        if absolute_path in directory.dir_path:
            db.session.delete(directory)
            for file in directory.files:
                db.session.delete(file)
            db.session.commit()
            


@app.route("/delete", methods=['GET', 'POST'])
def delete():
    del_data = request.args.get('path')
    dirs = current_user.directorys
    del_obj = del_data.split("/")[-1]
    if "." in del_data:#file
        for directory in dirs:
            for file in directory.files:
                if str(del_obj) == str(file.file_name+"."+file.file_ext):
                    db.session.delete(file)
                    db.session.commit()
    else:#folder
        delete_childs(del_data)
        for directory in dirs:
            if str(del_obj) == str(directory.dir_name):
                db.session.delete(directory)
                db.session.commit()
    return redirect("/")




@app.route("/logout")
def logout():
    login_user()
    return redirect(url_for("home"))