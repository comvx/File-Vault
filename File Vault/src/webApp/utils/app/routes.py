import os, sys
import secrets
import json, time
import base64
import uuid

from flask import render_template, url_for, flash, redirect, request, abort, make_response, Response, send_file
from flask_login import login_user, current_user, logout_user, login_required

from werkzeug.utils import secure_filename
from io import BytesIO

from webApp.utils.authentication.database.table import User, File, Directory, Vault, Share
from webApp.utils.app import *
from webApp.utils.app.forms import auth, data_upload, home_form, credit_card
from webApp.utils.cryptographie import hash, encrypt, decrypt
from webApp.utils.authentication import Credentials
from webApp.utils.authentication.generator import gen_user_id, gen_Pass
from webApp.utils.data import *
from webApp import *

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

@app.route("/")
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
            flash("Username does already exists!")
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

                time.sleep(1.7)
                return redirect("/home?path=")
            else:
                time.sleep(1.7)
                flash("Wrong username and/or password")
                return render_template('login.html', form=form, style_bg_status=style_bg_status_red)
        except Exception as identifier:
            time.sleep(1.7)
            flash("Wrong username and/or password")
            return render_template('login.html', form=form, style_bg_status=style_bg_status_red)
    return render_template('login.html', form=form, style_bg_status=style_bg_status_blue)

def transform_dataset(absolute_path):
    if current_user.is_authenticated:
        dirs = current_user.directorys

        output = list()
        try:
            for directory in dirs:
                if str(directory.dir_path) == str(absolute_path):
                    session_name = current_user.user_manager_id + current_user.username + current_user.get_id()
                    for file in directory.files:
                        try:
                            if file.file_share == False:
                                data_set = dataset(decrypt(file.file_name, session[session_name+"key"], session[session_name+"iv"]).decode(), decrypt(file.file_ext, session[session_name+"key"], session[session_name+"iv"]).decode(), directory.dir_path, file.file_data, directory.dir_path+"/"+file.file_name, file.file_name, "")
                                output.append(data_set.data_set)
                        except Exception as e:
                            pass
                    for vault in directory.vaults:
                        if vault.vault_share == False:
                            data_set = dataset(decrypt(vault.vault_name, session[session_name+"key"], session[session_name+"iv"]).decode(), "vault", directory.dir_path, "::", directory.dir_path + "/" + vault.vault_name, vault.vault_name, "")
                            output.append(data_set.data_set)
                if directory.dir_path.count("/") > absolute_path.count("/") and directory.dir_path.startswith(absolute_path):
                    if absolute_path.count("/") > 0:
                        if directory.dir_path.split("/")[1] == absolute_path.split("/")[1]:
                            child_dir = directory.dir_path.replace(absolute_path, "", 1)
                            if len(child_dir.split("/")) == 2:
                                data_set = dataset(directory.dir_name, "folder", directory.dir_path, "", directory.dir_path, "", directory.file_count)
                                output.append(data_set.data_set)
                    else:
                        if directory.dir_path.count("/") < 2:
                            data_set = dataset(directory.dir_name, "folder", directory.dir_path, "", directory.dir_path, "", directory.file_count)
                            output.append(data_set.data_set)
        except KeyError as e:
            flash("Logout timer expired")
            return redirect(url_for('logout'))
        return output
    else:
        flash("Logout timer expired")
        return redirect("/")

def check_for_twice_name(path, name):
    dirs = current_user.directorys
    for directory in dirs:
        if str(directory.dir_path) == str(path+"/"+name):
            return False
    return True

def duplicates_folder(folder_name, current_path):
    dirs = current_user.directorys
    new_path = current_path+"/"+folder_name
    for directory in dirs:
        if str(directory.dir_path) == str(new_path):
            return False
    return True

def duplicates_vault(vault_name, current_path):
    dirs = current_user.directorys
    new_path = current_path+"/"+vault_name
    for directory in dirs:
        for vault in directory.vaults:
            if str(directory.dir_path+"/"+vault.vault_name) == str(new_path):
                return False
    return True

def duplicates_file(file_name, current_path):
    dirs = current_user.directorys
    new_path = current_path+"/"+file_name
    for directory in dirs:
        for file in directory.files:
            if str(directory.dir_path+"/"+file.file_name) == str(new_path):
                return False
    return True


def check_validator(fields):
    for field in fields:
        if field == "" or field == " ":
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
                    if duplicates_folder(home_add.folder_name_input.data, calling_path):
                        new_dir = Directory(dir_name=home_add.folder_name_input.data, dir_path=calling_path+"/"+home_add.folder_name_input.data, user=current_user)
                        db.session.add(new_dir)
                        db.session.commit()
                        flash(f'Folder {home_add.folder_name_input.data} was added!')
                    else:
                        flash(f'Folder does already exists!')
        if vault_add.validate_on_submit():
            if vault_add.submit:
                if check_validator({vault_add.vault_name.data, vault_add.vault_username.data}):
                    try:
                        session_name = current_user.user_manager_id + current_user.username + current_user.get_id()
                        directory = get_dir_by_path(calling_path)
                        if directory != None:
                            enc_vault_name = encrypt(vault_add.vault_name.data.encode(), session[session_name+"key"], session[session_name+"iv"]).decode()
                            if duplicates_vault(enc_vault_name, calling_path):
                                new_vault = Vault(vault_name=enc_vault_name, vault_username=encrypt(vault_add.vault_username.data.encode(), session[session_name+"key"], session[session_name+"iv"]).decode(), vault_password=encrypt(vault_add.vault_password.data.encode(), session[session_name+"key"], session[session_name+"iv"]).decode())
                                directory.vaults.append(new_vault)
                                directory.file_count += 1
                                db.session.commit()
                                vault_add.vault_name.data = ""
                                vault_add.vault_username.data = ""
                                vault_add.vault_password.data = ""
                                flash(f'Vault {vault_add.vault_name.data} was added!')
                            else:
                                vault_add.vault_name.data = ""
                                vault_add.vault_username.data = ""
                                vault_add.vault_password.data = ""
                                flash(f'Vault does already exists!')
                        else:
                            flash(f'First, create a folder!')
                    except KeyError as e:
                        flash("Logout timer expired")
                        return redirect(url_for('logout'))

        dataset = transform_dataset(calling_path)

        calling_path_splitter = list()
        calling_path_splitter = calling_path.split("/")
        calling_path_splitter[0] = "/"
        if type(dataset) == Response:
            return dataset
        try:
            if len(dataset) < 1:
                return render_template('home.html', data_set=dataset, home_add=home_add, current_folder_path=absolute_path, current_folders=calling_path_splitter, current_folder_href=calling_path, vault_add=vault_add, nothingfound="block")
            else:
                return render_template('home.html', data_set=dataset, home_add=home_add, current_folder_path=absolute_path, current_folders=calling_path_splitter, current_folder_href=calling_path, vault_add=vault_add, nothingfound="none")
        except Exception as e:
            return dataset
    else:
        flash("Logout timer expired")
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
                            directory.file_count += 1
                            db.session.commit()
                        time.sleep(5)
                        #flash(f'File {file_name} was uploaded!')
                        return index_path(calling_path)
                    except KeyError as e:
                        flash("Logout timer expired")
                        return redirect(url_for('logout'))
            else:
                flash(f'First, create a folder!')
        return render_template("upload.html", form=form)
    else:
        flash("Logout timer expired")
        return redirect(url_for("login"))

def get_vault_by_name(vault_name, dir):
    for vault in dir.vaults:
        if str(vault.vault_name) == str(vault_name):
            return vault
    return None

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
                            
                            return Response(data_file, mimetype=mimetypes.types_map["."+data_ext.lower()])
            return redirect(url_for("login"))
        except KeyError as e:
            flash("Logout timer expired")
            return redirect(url_for('logout'))
    else:
        flash("Logout timer expired")
        return redirect(url_for("login"))

def convert_to_path(filePath):
    index = filePath.rindex("/")
    return filePath[0:index]

def get_file_from_dir(dir, file_name):
    for file in dir.files:
        if str(file_name) == str(file.file_name):
            return file
    return None

def valid_uuid(uuid):
    users = User.query.all()
    for user in users:
        for share in user.shares:
            if str(share.uuid) == str(uuid):
                return valid_uuid(uuid.uuid4())
    return uuid

def get_share_item(uuid):
    for user in User.query.all():
        for share in user.shares:
            if str(share.uuid) == str(uuid):
                return share, user
    return None

def get_dir_by_path_diff_user(path, user):
    dirs = user.directorys
    for directory in dirs:
        if str(directory.dir_path) == str(path):
            return directory
    return None

@app.route("/share", methods=['GET', 'POST'])
def share():
    action = request.args.get('a')
    if action == "use":
        print("d")
        uuid_client = request.args.get('uuid')
        share_item = get_share_item(uuid_client)
        if share_item != None:
            if str(uuid_client) == str(share_item[0].uuid):
                dir_path = convert_to_path(share_item[0].href)
                dest_dir = get_dir_by_path_diff_user(convert_to_path(share_item[0].href), share_item[1])
                if dest_dir != None:
                    file = get_file_from_dir(dest_dir, share_item[0].href.split("/")[-1])
                    db.session.delete(share_item[0])
                    db.session.commit()
                    return share_open(file, uuid_client)
    elif action == "create":
        if current_user.is_authenticated:
            focused_file_path = request.args.get('file_path')
            focused_file_path_dir = convert_to_path(focused_file_path)
            if focused_file_path_dir != None:
                dest_dir = get_dir_by_path(focused_file_path_dir)
                if dest_dir != None:
                    focused_file = get_file_from_dir(dest_dir, focused_file_path.split("/")[-1])
                    if focused_file != None:
                        created_uuid = valid_uuid(uuid.uuid4())

                        iv = pad(str(created_uuid), 20).encode()

                        session_name = current_user.user_manager_id + current_user.username + current_user.get_id()

                        original_file_name = decrypt(focused_file.file_name.encode(), session[session_name+"key"], session[session_name+"iv"]).decode()
                        original_file_ext = decrypt(focused_file.file_ext.encode(), session[session_name+"key"], session[session_name+"iv"]).decode()
                        original_file_data = decrypt(focused_file.file_data.encode(), session[session_name+"key"], session[session_name+"iv"])

                        share_file_name = encrypt(original_file_name.encode(), str(created_uuid), iv).decode()

                        copy_share_file = new_file = File(file_name=share_file_name, file_ext=encrypt(original_file_ext.encode(), str(created_uuid), iv).decode(), file_data=encrypt(original_file_data, str(created_uuid), iv).decode(), file_share=True)

                        dest_dir.files.append(copy_share_file)
                        new_share = Share(uuid=str(created_uuid), href=focused_file_path_dir+"/"+share_file_name, user=current_user)
                        db.session.add(new_share)
                        db.session.commit()
                        flash("172.105.247.216/share?a=use&uuid="+str(created_uuid))
                        return redirect("/")
    return "FUCK YOU!"

@app.route("/share_open")
def share_open(file, uuid):
    iv = pad(str(uuid), 20).encode()

    file_name = decrypt(file.file_name.encode(), str(uuid), iv).decode()
    file_ext = decrypt(file.file_ext.encode(), str(uuid), iv).decode()
    file_data = decrypt(file.file_data.encode(), str(uuid), iv)

    db.session.delete(file)
    db.session.commit()

    return Response(file_data, mimetype=mimetypes.types_map["."+file_ext.lower()])

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
    if current_user.is_authenticated:
        data_path = request.args.get('path')
        data_type = request.args.get('type')

        dirs = current_user.directorys
        del_obj = data_path.split("/")[-1]

        if data_type == "vault":
            splitter_index_dir_path = data_path.rindex("/")
            directory = get_dir_by_path(data_path[:splitter_index_dir_path])
            if directory != None:
                vault = get_vault_by_name(data_path[splitter_index_dir_path+1:], directory)
                if vault != None:
                    db.session.delete(vault)
                    directory.file_count -= 1
                    db.session.commit()
                    flash(f'Vault was deleted!')
        elif data_type != "folder" and data_type != "vault":#file
            splitter_index_dir_path = data_path.rindex("/")
            directory = get_dir_by_path(data_path[:splitter_index_dir_path])
            for file in directory.files:
                if str(data_path[splitter_index_dir_path+1:]) == str(file.file_name):
                    db.session.delete(file)
                    directory.file_count -= 1
                    db.session.commit()
                    flash(f'File was deleted!')
        else:#folder
            for directory in dirs:
                if str(data_path) == str(directory.dir_path):
                    for file in directory.files:
                        db.session.delete(file)
                    for vault in directory.vaults:
                        db.session.delete(vault)
                    db.session.delete(directory)
                    db.session.commit()
                    flash(f'Folder {directory.dir_name[:19]} was deleted!')
        return index_path(data_path[:data_path.rindex("/")])
    else:
        flash("Logout timer expired")
        return redirect(url_for("index"))

@app.route("/rename")
def rename():
    if current_user.is_authenticated:
        dir_focused = request.args.get('path')
        new_field_name = request.args.get('new_name')
        data_type = request.args.get('type')
        if data_type == "folder":
            dir = get_dir_by_path(dir_focused)
            if dir != None:
                splitter_index_dir_path = dir_focused.rindex("/")
                if duplicates_folder(new_field_name, dir_focused[:splitter_index_dir_path]):
                    dir.dir_name = new_field_name

                    splitter_index_dir_path = dir.dir_path.rindex("/")
                    new_dir_href = dir.dir_path[:splitter_index_dir_path] + "/" + new_field_name
                    dir.dir_path = new_dir_href
                    db.session.commit()
                    flash(f'Folder renamed to {new_field_name[:19]}.. !')

                else:
                    flash(f'Folder does already exists!')
        elif data_type == "vault":
            splitter_index_dir_path = dir_focused.rindex("/")
            dir = get_dir_by_path(dir_focused[:splitter_index_dir_path])
            if dir != None:
                print(dir_focused[splitter_index_dir_path:])
                vault = get_vault_by_name(dir_focused[splitter_index_dir_path+1:], dir)
                if vault != None:
                    session_name = current_user.user_manager_id + current_user.username + current_user.get_id()
                    new_enc_name = encrypt(new_field_name.encode(), session[session_name+"key"], session[session_name+"iv"]).decode()
                    if duplicates_vault(new_enc_name, dir_focused[:splitter_index_dir_path]):
                        vault.vault_name = new_enc_name
                        db.session.commit()
                        flash(f'Vault renamed to {new_field_name[:19]}.. !')
                    else:
                        flash(f'Vault does already exists!')
        elif data_type == "file":
            splitter_index_dir_path = dir_focused.rindex("/")
            dir = get_dir_by_path(dir_focused[:splitter_index_dir_path])
            if dir != None:
                print(dir_focused[splitter_index_dir_path+1:])
                file = get_file_from_dir(dir, dir_focused[splitter_index_dir_path+1:])
                if file != None:
                    session_name = current_user.user_manager_id + current_user.username + current_user.get_id()
                    new_enc_name = encrypt(new_field_name.encode(), session[session_name+"key"], session[session_name+"iv"]).decode()
                    if duplicates_file(new_enc_name, dir_focused[:splitter_index_dir_path]):
                        file.file_name = new_enc_name
                        db.session.commit()
                        flash(f'File renamed to {new_field_name[:19]}.. !')
                    else:
                        flash(f'File does already exists!')


        index_from_splitter = dir_focused.rindex("/")
        new_redirect = dir_focused[:index_from_splitter]
        return index_path(new_redirect)
    else:
        flash("Logout timer expired")
        return redirect(url_for('index'))

@app.route("/download")
def download():
    req_file = request.args.get('file')
    if current_user.is_authenticated:
        if req_file != None or req_file != "":
            splitter_index_dir_path = req_file.rindex("/")
            dir = get_dir_by_path(req_file[:splitter_index_dir_path])
            if dir != None:
                session_name = current_user.user_manager_id + current_user.username + current_user.get_id()
                file = get_file_from_dir(dir, req_file[splitter_index_dir_path+1:])
                if file != None:
                    file_data = decrypt(file.file_data, session[session_name+"key"], session[session_name+"iv"])
                    file_name = decrypt(file.file_name, session[session_name+"key"], session[session_name+"iv"]).decode()
                    return send_file(BytesIO(file_data), attachment_filename=file_name, as_attachment=True)
    else:
        flash("Logout timer expired")
        return redirect(url_for("index"))
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    logout_user()
    flash("Sucessfully logout")
    return redirect(url_for("home"))