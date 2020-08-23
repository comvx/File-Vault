import os, sys
import secrets
import json, time

from flask import render_template, url_for, flash, redirect, request, abort, make_response, Response
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from werkzeug.utils import secure_filename

from Vault.utils.authentication.database.table import User, File, Directory, Vault
from Vault.utils.app import *
from Vault.utils.app.forms import auth, data_upload, home_form, credit_card
from Vault.utils.cryptographie import hash, encrypt, decrypt
from Vault.utils.authentication import Credentials
from Vault.utils.authentication.generator import gen_user_id, gen_Pass
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

@app.route("/<string:path>")
def index_path(path):
    if current_user.is_authenticated:
        return redirect("/home?path="+path)
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

            session_name = current_user.user_manager_id + current_user.username + current_user.get_id()
            session[session_name+"salt"] = secret_key[16:]
            session[session_name+"iv"] = secret_key[0:16]
            session[session_name+"key"] = authentication.gen_key(secret_key, session[session_name+"salt"])

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

                session_name = current_user.user_manager_id + current_user.username + current_user.get_id()
                session[session_name+"salt"] = secret_key[16:]
                session[session_name+"iv"] = secret_key[0:16]
                session[session_name+"key"] = authentication.gen_key(secret_key, session[session_name+"salt"])

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

def transform_dataset(absolute_path):
    dirs = current_user.directorys

    output = list()
    try:
        for directory in dirs:
            if str(directory.dir_path) == str(absolute_path):
                session_name = current_user.user_manager_id + current_user.username + current_user.get_id()
                for file in directory.files:
                    data_set = dataset(decrypt(file.file_name, session[session_name+"key"], session[session_name+"iv"]).decode(), decrypt(file.file_ext, session[session_name+"key"], session[session_name+"iv"]).decode(), directory.dir_path, file.file_data, directory.dir_path+"/"+file.file_name, file.file_name)
                    output.append(data_set.data_set)
                for vault in directory.vaults:
                    data_set = dataset(decrypt(vault.vault_name, session[session_name+"key"], session[session_name+"iv"]).decode(), "vault", directory.dir_path, "::", directory.dir_path + "/" + vault.vault_name, vault.vault_name)
                    output.append(data_set.data_set)
            if directory.dir_path.count("/") > absolute_path.count("/") and directory.dir_path.startswith(absolute_path):
                if absolute_path.count("/") > 0:
                    if directory.dir_path.split("/")[1] == absolute_path.split("/")[1]:
                        child_dir = directory.dir_path.replace(absolute_path, "", 1)
                        if len(child_dir.split("/")) == 2:
                            data_set = dataset(directory.dir_name, "folder", directory.dir_path, "", directory.dir_path, "")
                            output.append(data_set.data_set)
                else:
                    if directory.dir_path.count("/") < 2:
                        data_set = dataset(directory.dir_name, "folder", directory.dir_path, "", directory.dir_path, "")
                        output.append(data_set.data_set)
    except KeyError as e:
        return redirect(url_for('logout'))
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

        absolute_path = calling_path
        
        home = home_form()

        vault_add = home.vault_add()
        home_add = home.add()

        current_folder_path = ""

        if home_add.validate_on_submit():
            if home_add.submit:
                if len(home_add.folder_name_input.data) > 0:
                    if duplicates(home_add.folder_name_input.data, calling_path):
                        new_dir = Directory(dir_name=home_add.folder_name_input.data, dir_path=calling_path+"/"+home_add.folder_name_input.data, user=current_user)
                        db.session.add(new_dir)
                        db.session.commit()
        if vault_add.validate_on_submit():
            if vault_add.submit:
                try:
                    session_name = current_user.user_manager_id + current_user.username + current_user.get_id()
                    directory = get_dir_by_path(calling_path)
                    if directory != None:
                        new_vault = Vault(vault_name=encrypt(vault_add.vault_name.data.encode(), session[session_name+"key"], session[session_name+"iv"]).decode(), vault_username=encrypt(vault_add.vault_username.data.encode(), session[session_name+"key"], session[session_name+"iv"]).decode(), vault_password=encrypt(vault_add.vault_password.data.encode(), session[session_name+"key"], session[session_name+"iv"]).decode())
                        directory.vaults.append(new_vault)
                        db.session.commit()
                except KeyError as e:
                    return redirect(url_for('logout'))

        dataset = transform_dataset(calling_path)

        calling_path_splitter = calling_path.split("/")
        return render_template('home.html', data_set=dataset, home_add=home_add, current_folder_path=absolute_path, current_folders=calling_path_splitter, current_folder_href=calling_path, vault_add=vault_add)
    else:
        return redirect(url_for("login"))

def get_dir_by_path(path):
    dirs = current_user.directorys
    for directory in dirs:
        if str(directory.dir_path) == str(path):
            return directory
    return None

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if current_user.is_authenticated:
        form = data_upload()
        calling_path = request.args.get('path')
        if form.validate_on_submit():
            directory = get_dir_by_path(calling_path)
            if directory != None:
                files = request.files.getlist(form.data.name)
                if files:
                    try:
                        session_name = current_user.user_manager_id + current_user.username + current_user.get_id()
                        for file in files:
                            file_contents = encrypt(file.stream.read(), session[session_name+"key"], session[session_name+"iv"])
                            file_name = secure_filename(file.filename)
                            file_ext = file_name.split(".")[-1]
                            
                            new_file = File(file_name=encrypt(file_name.encode(), session[session_name+"key"], session[session_name+"iv"]).decode(), file_ext=encrypt(file_ext.encode(), session[session_name+"key"], session[session_name+"iv"]).decode(), file_data=file_contents.decode())
                            directory.files.append(new_file)
                            db.session.commit()
                        time.sleep(5)
                        return index_path(calling_path)
                    except KeyError as e:
                        return redirect(url_for('logout'))
        return render_template("upload.html", form=form)
    else:
        return redirect(url_for("login"))

def get_vault_by_name(vault_name, dir):
    for vault in dir.vaults:
        if str(vault.vault_name) == str(vault_name):
            return vault
    return None

def get_data(data, ptype):
    length = str(len(data)).encode()
    while True:
        yield(b'--frame\r\n'
              b'Content-Type: ' + ptype.encode() + b'\r\n'
              b'Content-Length: ' + length + b'\r\n'
              b'\r\n'+ data + b'\r\n')
        time.sleep(0.01)

@app.route("/open", methods=['GET', 'POST'])
def open():
    if current_user.is_authenticated:
        data_name = request.args.get('name')
        data_path = request.args.get('path')
        data_type = request.args.get('type')

        form = credit_card()
        try:
            session_name = current_user.user_manager_id + current_user.username + current_user.get_id()

            if form.validate_on_submit():
                if form.generate:
                    new_pass = gen_Pass()
                    directory = get_dir_by_path(data_path)
                    if directory != None:
                        vault = get_vault_by_name(data_name, directory)
                        if vault != None:
                            vault.vault_password = encrypt(new_pass.encode(), session[session_name+"key"], session[session_name+"iv"]).decode()
                            db.session.commit()
            del form

            if data_type == "vault":
                directory = get_dir_by_path(data_path)
                if directory != None:
                    vault = get_vault_by_name(data_name, directory)
                    if vault != None:
                        form = credit_card()
                        vault_set = vaultset(decrypt(vault.vault_name, session[session_name+"key"], session[session_name+"iv"]).decode(), decrypt(vault.vault_username, session[session_name+"key"], session[session_name+"iv"]).decode(), decrypt(vault.vault_password, session[session_name+"key"], session[session_name+"iv"]).decode(), vault.id)
                        return render_template("card.html", data=vault_set.data_set, form=form, return_value="/home?path="+data_path)
            else:
                directory = get_dir_by_path(data_path)
                if directory != None:
                    for file in directory.files:
                        if str(file.file_name) == str(data_name):
                            data_file = decrypt(file.file_data, session[session_name+"key"], session[session_name+"iv"])
                            data_ext = decrypt(file.file_ext, session[session_name+"key"], session[session_name+"iv"]).decode()
                            return Response(get_data(data_file, mimetypes.types_map["."+data_ext]), mimetype=mimetypes.types_map["."+data_ext])
            return redirect(url_for("login"))
        except KeyError as e:
            return redirect(url_for('logout'))
    else:
        return redirect(url_for("login"))

def delete_childs(absolute_path):
    dirs = current_user.directorys
    for directory in dirs:
        if absolute_path in directory.dir_path:
            db.session.delete(directory)
            for file in directory.files:
                db.session.delete(file)
            db.session.commit()

def get_all_files():
    dirs = current_user.directorys
    output = list()
    for directory in dirs:
        for file in directory.files:
            output.append(file)
    return output

def is_file(file_name):
    for file in get_all_files():
        if str(file.file_name) == str(file_name):
            return True
    return False

@app.route("/delete", methods=['GET', 'POST'])
def delete():
    data_path = request.args.get('path')
    enc_name_file = request.args.get('enc_name')
    data_type = request.args.get('type')

    dirs = current_user.directorys
    del_obj = data_path.split("/")[-1]

    if data_type == "vault":
        directory = get_dir_by_path(data_path)
        vault = get_vault_by_name(enc_name_file, directory)
        db.session.delete(vault)
        db.session.commit()
    elif data_type != "folder" and data_type != "vault":
        for directory in dirs:
            if str(directory.dir_path) == str(data_path):
                for file in directory.files:
                    print(file.file_name)
                    print(str(enc_name_file))
                    if str(enc_name_file) == str(file.file_name):
                        print("2")
                        db.session.delete(file)
                        db.session.commit()
    else:#folder
        delete_childs(data_path)
        for directory in dirs:
            if str(del_obj) == str(directory.dir_name):
                db.session.delete(directory)
                db.session.commit()
    return index_path(data_path)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))