import os, sys
import secrets
import json, time
import base64
import uuid

from flask import render_template, url_for, flash, redirect, request, abort, make_response, Response, send_file
from flask_login import login_user, current_user, logout_user, login_required

from werkzeug.utils import secure_filename
from io import BytesIO
import shutil

from webApp.utils.authentication.database.table import User, File, Directory, Vault, Share, Config
from webApp.utils.app import *
from webApp.utils.app.forms import auth, data_upload, home_form, credit_card
from webApp.utils.cryptographie import hash, encrypt, decrypt
from webApp.utils.authentication import Credentials
from webApp.utils.authentication.generator import gen_user_id, gen_Pass, gen_String
from webApp.utils.data import *
from webApp import *

style_bg_status_blue = 'background: linear-gradient(135deg, #080808 0%, #20272f 100%); '
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
    form = auth.register()
    if form.validate_on_submit():
        if(form.password_input_re.data == form.password_input.data):
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
                current_user.temp = list()

                del hashed_username
                del hashed_master_password
                del user

                return redirect(url_for('index'))
            else:
                return render_template('register.html', form=form, style_bg_status=style_bg_status_red)
        else:
            flash("Passwords does not match!")
            return render_template('register.html', form=form, style_bg_status=style_bg_status_red)
    return render_template('register.html', form=form, style_bg_status=style_bg_status_blue)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/")
    form = auth.login()
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
                current_user.temp = list()
                del hashed_username
                del hashed_master_password
                del user

                return redirect("/home?path=")
            else:
                flash("Wrong username and/or password")
                return render_template('login.html', form=form, style_bg_status=style_bg_status_red)
        except Exception as identifier:
            flash("Wrong username and/or password")
            return render_template('login.html', form=form, style_bg_status=style_bg_status_red)
    return render_template('login.html', form=form, style_bg_status=style_bg_status_blue)

def transform_dataset(absolute_path):
    if current_user.is_authenticated:
        dirs = current_user.directorys
        session_name = current_user.user_manager_id + current_user.username + current_user.get_id()
        output = list()
        try:
            for directory in dirs:
                dir_path = decrypt(directory.dir_path, session[session_name+"key"], session[session_name+"iv"]).decode()
                if str(dir_path) == str(absolute_path):
                    for file in directory.files:
                        try:
                            if file.file_share == False:
                                data_set = dataset(decrypt(file.file_name, session[session_name+"key"], session[session_name+"iv"]).decode(), decrypt(file.file_ext, session[session_name+"key"], session[session_name+"iv"]).decode(), dir_path, file.file_data, dir_path+"/"+file.file_name, file.file_name, "")
                                output.append(data_set.data_set)
                        except Exception as e:
                            pass
                    for vault in directory.vaults:
                        if vault.vault_share == False:
                            data_set = dataset(decrypt(vault.vault_name, session[session_name+"key"], session[session_name+"iv"]).decode(), "vault", dir_path, "::", dir_path + "/" + vault.vault_name, vault.vault_name, "")
                            output.append(data_set.data_set)
                if dir_path.count("/") > absolute_path.count("/") and dir_path.startswith(absolute_path):
                    if absolute_path.count("/") > 0:
                        if dir_path.split("/")[1] == absolute_path.split("/")[1]:
                            child_dir = dir_path.replace(absolute_path, "", 1)
                            if len(child_dir.split("/")) == 2:
                                dir_name = decrypt(directory.dir_name, session[session_name+"key"], session[session_name+"iv"]).decode()
                                data_set = dataset(dir_name, "folder", dir_path, "", dir_path, "", directory.file_count)
                                output.append(data_set.data_set)
                    else:
                        if dir_path.count("/") < 2:
                            dir_name = decrypt(directory.dir_name, session[session_name+"key"], session[session_name+"iv"]).decode()
                            data_set = dataset(dir_name, "folder", dir_path, "", dir_path, "", directory.file_count)
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
    session_name = current_user.user_manager_id + current_user.username + current_user.get_id()
    for directory in dirs:
        dir_path = decrypt(directory.dir_path, session[session_name+"key"], session[session_name+"iv"]).decode()
        if str(dir_path) == str(path+"/"+name):
            return False
    return True

def duplicates_folder(folder_name, current_path):
    dirs = current_user.directorys
    new_path = current_path+"/"+folder_name
    session_name = current_user.user_manager_id + current_user.username + current_user.get_id()
    for directory in dirs:
        dir_path = decrypt(directory.dir_path, session[session_name+"key"], session[session_name+"iv"]).decode()
        if str(dir_path) == str(new_path):
            return False
    return True

def duplicates_vault(vault_name, current_path):
    dirs = current_user.directorys
    new_path = current_path+"/"+vault_name
    session_name = current_user.user_manager_id + current_user.username + current_user.get_id()
    for directory in dirs:
        for vault in directory.vaults:
            dir_path = decrypt(directory.dir_path, session[session_name+"key"], session[session_name+"iv"]).decode()
            if str(dir_path+"/"+vault.vault_name) == str(new_path):
                return False
    return True

def duplicates_file(file_name, current_path):
    dirs = current_user.directorys
    new_path = current_path+"/"+file_name
    session_name = current_user.user_manager_id + current_user.username + current_user.get_id()
    for directory in dirs:
        for file in directory.files:
            dir_path = decrypt(directory.dir_path, session[session_name+"key"], session[session_name+"iv"]).decode()
            if str(dir_path+"/"+file.file_name) == str(new_path):
                return False
    return True


def check_validator(fields):
    for field in fields:
        if field == "" or field == " ":
            return False
    return True

def search_for_content(dir, name):
    session_name = current_user.user_manager_id + current_user.username + current_user.get_id()
    content_name = encrypt(name.encode(), session[session_name+"key"], session[session_name+"iv"])

    files = dir.files
    vaults = dir.vaults
    output = list()

    for file in files:
        if(file.file_name == content_name and file.file_share == False):
            output.append(file)
    for vault in vaults:
        if(vault.vault_name == content_name and vault.vault_share == False):
            output.append(vault)
    for directory in current_user.directorys:
        dir_path = decrypt(dir.dir_path, session[session_name+"key"], session[session_name+"iv"]).decode()
        directory_path = decrypt(directory.dir_path, session[session_name+"key"], session[session_name+"iv"]).decode()
        index = directory_path.rindex("/")
        if(directory_path[0:index] == dir_path and directory.dir_name == content_name):
            output.append(directory)
    return output

def transform_content_to_set(contents, dir):
    output = list()
    session_name = current_user.user_manager_id + current_user.username + current_user.get_id()
    dir_path = None
    if(type(dir) == Directory):
        dir_path = decrypt(dir.dir_path, session[session_name+"key"], session[session_name+"iv"]).decode()
    else:
        dir_path = dir

    for content in contents:
        if(type(content) == Vault):
            data_set = dataset(decrypt(content.vault_name, session[session_name+"key"], session[session_name+"iv"]).decode(), "vault", dir_path, "::", dir_path + "/" + content.vault_name, content.vault_name, "")
            output.append(data_set.data_set)
        if(type(content) == File):
            data_set = dataset(decrypt(content.file_name, session[session_name+"key"], session[session_name+"iv"]).decode(), decrypt(content.file_ext, session[session_name+"key"], session[session_name+"iv"]).decode(), dir_path, content.file_data, dir_path+"/"+content.file_name, content.file_name, "")
            output.append(data_set.data_set)
        if(type(content) == Directory):
            dir_name = decrypt(content.dir_name, session[session_name+"key"], session[session_name+"iv"]).decode()
            data_set = dataset(dir_name, "folder", dir_path, "", dir_path, "", content.file_count)
            output.append(data_set.data_set)
    return output

def get_dir_by_path(path):
    dirs = current_user.directorys
    session_name = current_user.user_manager_id + current_user.username + current_user.get_id()
    for directory in dirs:
        dir_path = decrypt(directory.dir_path, session[session_name+"key"], session[session_name+"iv"]).decode()
        print(dir_path)
        if str(dir_path) == str(path):
            return directory
    return None

def get_dirs_by_path(path):
    dirs = current_user.directorys
    session_name = current_user.user_manager_id + current_user.username + current_user.get_id()
    output = list()
    for directory in dirs:
        dir_path = decrypt(directory.dir_path, session[session_name+"key"], session[session_name+"iv"]).decode()
        if str(dir_path) == str(path):
            output.append(directory)
    return output

def search(search_path, search_request):
    if(len(search_request) < 1):
            return index_path(search_path)
    elif(len(search_path) > 0):
        dir = get_dir_by_path(search_path)
        if(dir != None):
            search_results = search_for_content(dir, search_request)
            output_results = transform_content_to_set(search_results, dir)
            return output_results
    elif(len(search_path) < 1):
        dirs = get_dirs_by_path("/"+search_request)
        if(len(dirs) > 0):
            output_results = transform_content_to_set(dirs, "/"+search_request)
            return output_results
    return list()

@app.route("/home", methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated:
        calling_path = request.args.get('path')
        
        absolute_path = calling_path

        search_path = request.args.get('search_dir')
        search_request = request.args.get('search_input')

        home = home_form()

        vault_add = home.vault_add()
        home_add = home.add()
        controller_form = home.controller()

        current_folder_path = ""

        session_name = current_user.user_manager_id + current_user.username + current_user.get_id()

        if home_add.validate_on_submit():
            if home_add.submit:
                if len(home_add.folder_name_input.data) > 0:
                    if duplicates_folder(home_add.folder_name_input.data, calling_path):
                        new_dir = Directory(dir_name=encrypt((home_add.folder_name_input.data).encode(), session[session_name+"key"], session[session_name+"iv"]), dir_path=encrypt((calling_path+"/"+home_add.folder_name_input.data).encode(), session[session_name+"key"], session[session_name+"iv"]), user=current_user)
                        db.session.add(new_dir)
                        db.session.commit()
                        flash("Folder " + home_add.folder_name_input.data + " was added!")
                    else:
                        flash("Folder does already exists!")
        if vault_add.validate_on_submit():
            if vault_add.submit:
                if check_validator({vault_add.vault_name.data, vault_add.vault_username.data}):
                    try:
                        session_name = current_user.user_manager_id + current_user.username + current_user.get_id()
                        directory = get_dir_by_path(calling_path)
                        if directory != None:
                            enc_vault_name = encrypt(vault_add.vault_name.data.encode(), session[session_name+"key"], session[session_name+"iv"])
                            if duplicates_vault(enc_vault_name, calling_path):
                                new_vault = Vault(vault_name=enc_vault_name, vault_username=encrypt(vault_add.vault_username.data.encode(), session[session_name+"key"], session[session_name+"iv"]), vault_password=encrypt(vault_add.vault_password.data.encode(), session[session_name+"key"], session[session_name+"iv"]))
                                directory.vaults.append(new_vault)
                                directory.file_count += 1
                                db.session.commit()
                                vault_add.vault_name.data = ""
                                vault_add.vault_username.data = ""
                                vault_add.vault_password.data = ""
                                flash("Vault " + vault_add.vault_name.data + " was added!")
                            else:
                                vault_add.vault_name.data = ""
                                vault_add.vault_username.data = ""
                                vault_add.vault_password.data = ""
                                flash("Vault does already exists!")
                        else:
                            flash("First, create a folder!")
                    except KeyError as e:
                        flash("Logout timer expired")
                        return redirect(url_for('logout'))
        #SEARCH <START>
        if(search_path != None and search_request != None):
            calling_path_splitter = list()
            calling_path_splitter = search_path.split("/")
            calling_path_splitter[0] = "/"
            result = search(search_path, search_request)
            if len(result) < 1:
                return render_template('home.html', data_set=result, controller=controller_form ,home_add=home_add, current_folder_path=absolute_path, current_folders=calling_path_splitter, current_folder_href=calling_path, vault_add=vault_add, nothingfound="block", search="")
            else:
                return render_template('home.html', data_set=result, controller=controller_form , home_add=home_add, current_folder_path=absolute_path, current_folders=calling_path_splitter, current_folder_href=calling_path, vault_add=vault_add, nothingfound="none", search="")
        #SEARCH <END>
        else:
            dataset = transform_dataset(calling_path)

            calling_path_splitter = list()
            calling_path_splitter = calling_path.split("/")
            calling_path_splitter[0] = "/"

            if type(dataset) == Response:
                return dataset
            if len(dataset) < 1:
                return render_template('home.html', data_set=dataset, controller=controller_form ,home_add=home_add, current_folder_path=absolute_path, current_folders=calling_path_splitter, current_folder_href=calling_path, vault_add=vault_add, nothingfound="block", search="")
            else:
                return render_template('home.html', data_set=dataset, controller=controller_form , home_add=home_add, current_folder_path=absolute_path, current_folders=calling_path_splitter, current_folder_href=calling_path, vault_add=vault_add, nothingfound="none", search="")
        
        return "This should have not gonna happen :("
    else:
        flash("Logout timer expired")
        return redirect(url_for("login"))

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if current_user.is_authenticated:
        form = data_upload()
        return render_template("upload.html", form=form)
    else:
        flash("Logout timer expired")
        return redirect(url_for("login"))

@app.route("/uploadcontent", methods=['POST'])
def upload_chunk():
    if current_user.is_authenticated:
        session_name = current_user.user_manager_id + current_user.username + current_user.get_id()
        file = request.files['file']
        current_chunk = int(request.form['dzchunkindex'])
        total_chunks = int(request.form['dztotalchunkcount'])
        dest_Dir_config = request.form['destURL'].split("?")[1].split("=")[1]

        file_name_enc = encrypt(secure_filename(file.filename).encode(), session[session_name+"key"], session[session_name+"iv"])
        if(current_chunk == 0):
            app.permanent_session_lifetime = timedelta(days=31)
            random_name = gen_config_name()
            new_config = Config(name=random_name, file_name=file_name_enc, path=("/var/www/webApp/webApp/utils/data/"+str(current_user.id)+"/"+random_name+".json"), user=current_user)
            db.session.add(new_config)
            db.session.commit()

        config = get_config_by_name(file_name_enc)

        json_chunks = Chunks(config)
        json_chunks.addChunk(current_chunk, encrypt(file.stream.read(), session[session_name+"key"], session[session_name+"iv"]))
        json_chunks.saveJson(config)

        if(current_chunk == total_chunks-1):
            json_chunks.sortChunks()
            json_chunks.saveJson(config)

            enc_data = encrypt(json_chunks.getFileFDB(session_name, session), session[session_name+"key"], session[session_name+"iv"])
            enc_file_ext = encrypt(secure_filename(file.filename).split(".")[-1].encode(), session[session_name+"key"], session[session_name+"iv"])

            new_file = File(file_name=file_name_enc, file_ext=enc_file_ext, file_data=enc_data, file_share=False)

            os.remove(config.path)
            shutil.rmtree(config.path.replace("/"+config.name+".json", ""))

            dst_dir = get_dir_by_path(dest_Dir_config)
            if(dst_dir != None):
                dst_dir.files.append(new_file)
                dst_dir.file_count += 1
                db.session.delete(config)
                db.session.commit()
                app.permanent_session_lifetime = timedelta(minutes=5)
            else:
                return make_response(('error', 409))
        return make_response(('ok', 200))
    else:
        flash("Logout timer expired")
        return redirect(url_for("login"))

def get_config_by_name(filename):
    for config in current_user.config_data:
        if(config.file_name == filename):
            return config
    return None

def gen_config_name():
    name = gen_String(10,15)
    for config in current_user.config_data:
        if(config.name == name):
            return gen_config_name()
    return name

def get_vault_by_name(vault_name, dir):
    for vault in dir.vaults:
        if str(vault.vault_name) == str(vault_name):
            return vault
    return None

@app.route("/open", methods=['GET', 'POST'])
def open_content():
    if current_user.is_authenticated:
        data_name = request.args.get('name')
        data_path = request.args.get('path')
        data_type = request.args.get('type')

        print(data_name)

        form = credit_card()
        try:
            session_name = current_user.user_manager_id + current_user.username + current_user.get_id()

            if form.validate_on_submit():
                if form.submit:
                    new_pwd = form.password.data
                    directory = get_dir_by_path(data_path)
                    if directory != None:
                        vault = get_vault_by_name(data_name, directory)
                        if vault != None:
                            print(new_pwd)
                            vault.vault_password = encrypt(new_pwd.encode(), session[session_name+"key"], session[session_name+"iv"])
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
    session_name = current_user.user_manager_id + current_user.username + current_user.get_id()
    for directory in dirs:
        dir_path = decrypt(directory.dir_path, session[session_name+"key"], session[session_name+"iv"]).decode()
        if str(dir_path) == str(path):
            return directory
    return None


@app.route("/share", methods=['GET', 'POST'])
def share():
    action = request.args.get('a')
    if action == "use":
        uuid_client = request.args.get('uuid')
        uuid_type = request.args.get('type')
        share_item = get_share_item(uuid_client)
        if share_item != None:
            if str(uuid_client) == str(share_item[0].uuid):
                dir_path = convert_to_path(share_item[0].href)
                dest_dir = get_dir_by_path_diff_user(convert_to_path(share_item[0].href), share_item[1])
                if dest_dir != None:
                    if uuid_type == "vault":
                        vault = get_vault_by_name(share_item[0].href.split("/")[-1] ,dest_dir)
                        db.session.delete(share_item[0])
                        db.session.commit()
                        return share_open(vault, uuid_client, "vault")
                    elif uuid_type == "file":
                        file = get_file_from_dir(dest_dir, share_item[0].href.split("/")[-1])
                        db.session.delete(share_item[0])
                        db.session.commit()
                        return share_open(file, uuid_client, "file")
    elif action == "create":
        if current_user.is_authenticated:
            focused_file_path = request.args.get('file_path')
            focused_file_type = request.args.get('file_type')
            focused_file_path_dir = convert_to_path(focused_file_path)
            if focused_file_path_dir != None:
                dest_dir = get_dir_by_path(focused_file_path_dir)
                if dest_dir != None:
                    if focused_file_type == "vault":
                        focused_vault = get_vault_by_name(focused_file_path.split("/")[-1], dest_dir)
                        if focused_vault != None:
                            created_uuid = valid_uuid(uuid.uuid4())

                            iv = pad(str(created_uuid), 20).encode()

                            session_name = current_user.user_manager_id + current_user.username + current_user.get_id()

                            original_vault_name = decrypt(focused_vault.vault_name.encode(), session[session_name+"key"], session[session_name+"iv"]).decode()
                            original_vault_username = decrypt(focused_vault.vault_username.encode(), session[session_name+"key"], session[session_name+"iv"]).decode()
                            original_vault_password = decrypt(focused_vault.vault_password.encode(), session[session_name+"key"], session[session_name+"iv"]).decode()

                            share_vault_name = encrypt(original_vault_name.encode(), str(created_uuid), iv)

                            copy_share_vault = new_file = Vault(vault_name=share_vault_name, vault_username=encrypt(original_vault_username.encode(), str(created_uuid), iv), vault_password=encrypt(original_vault_password.encode(), str(created_uuid), iv), vault_share=True)

                            dest_dir.vaults.append(copy_share_vault)
                            new_share = Share(uuid=str(created_uuid), href=focused_file_path_dir+"/"+share_vault_name, user=current_user)
                            db.session.add(new_share)
                            db.session.commit()
                            flash("https://vault-manager.de/share?a=use&uuid="+str(created_uuid)+"&type=vault")
                            return index_path(dest_dir.dir_path)
                    elif focused_file_type == "file":
                        focused_file = get_file_from_dir(dest_dir, focused_file_path.split("/")[-1])
                        if focused_file != None:
                            created_uuid = valid_uuid(uuid.uuid4())

                            iv = pad(str(created_uuid), 20).encode()

                            session_name = current_user.user_manager_id + current_user.username + current_user.get_id()

                            original_file_name = decrypt(focused_file.file_name.encode(), session[session_name+"key"], session[session_name+"iv"]).decode()
                            original_file_ext = decrypt(focused_file.file_ext.encode(), session[session_name+"key"], session[session_name+"iv"]).decode()
                            original_file_data = decrypt(focused_file.file_data.encode(), session[session_name+"key"], session[session_name+"iv"])

                            share_file_name = encrypt(original_file_name.encode(), str(created_uuid), iv)

                            copy_share_file = new_file = File(file_name=share_file_name, file_ext=encrypt(original_file_ext.encode(), str(created_uuid), iv), file_data=encrypt(original_file_data, str(created_uuid), iv), file_share=True)

                            dest_dir.files.append(copy_share_file)
                            new_share = Share(uuid=str(created_uuid), href=focused_file_path_dir+"/"+share_file_name, user=current_user)
                            db.session.add(new_share)
                            db.session.commit()
                            flash("https://vault-manager.de/share?a=use&uuid="+str(created_uuid)+"&type=file")
                            return index_path(dest_dir.dir_path)
    return redirect(url_for("index"))

@app.route("/share_open")
def share_open(item, uuid, share_type):
    iv = pad(str(uuid), 20).encode()
    if share_type == "vault":
        vault_name = decrypt(item.vault_name.encode(), str(uuid), iv).decode()
        vault_username = decrypt(item.vault_username.encode(), str(uuid), iv).decode()
        vault_password = decrypt(item.vault_password.encode(), str(uuid), iv).decode()

        db.session.delete(item)
        db.session.commit()

        vault_set = vaultset(vault_name, vault_username, vault_password, item.id)
        form = credit_card()

        return render_template("card.html", data=vault_set.data_set, form=form, return_value="")
    elif share_type == "file":
        file_name = decrypt(item.file_name.encode(), str(uuid), iv).decode()
        file_ext = decrypt(item.file_ext.encode(), str(uuid), iv).decode()
        file_data = decrypt(item.file_data.encode(), str(uuid), iv)

        db.session.delete(item)
        db.session.commit()

        return Response(file_data, mimetype=mimetypes.types_map["."+file_ext.lower()])
    return redirect(url_for("index"))

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

def remDirsRec(startDirPath):
    session_name = current_user.user_manager_id + current_user.username + current_user.get_id()
    for directory in current_user.directorys:
        curr_dir_path = decrypt(directory.dir_path.encode(), session[session_name+"key"], session[session_name+"iv"]).decode()
        focus_element = curr_dir_path[0:len(startDirPath)]
        if focus_element == startDirPath:
            for file in directory.files:
                db.session.delete(file)
            for vault in directory.vaults:
                db.session.delete(vault)
            db.session.delete(directory)
            db.session.commit()

@app.route("/delete", methods=['GET', 'POST'])
def delete():
    if current_user.is_authenticated:
        session_name = current_user.user_manager_id + current_user.username + current_user.get_id()
        data_path = request.args.get('path')
        data_type = request.args.get('type')

        data_path_enc = encrypt(data_path.encode(), session[session_name+"key"], session[session_name+"iv"])

        dirs = current_user.directorys

        if data_type == "vault":
            splitter_index_dir_path = data_path.rindex("/")
            directory = get_dir_by_path(data_path[:splitter_index_dir_path])
            if directory != None:
                vault = get_vault_by_name(data_path[splitter_index_dir_path+1:], directory)
                if vault != None:
                    db.session.delete(vault)
                    directory.file_count -= 1
                    db.session.commit()
                    flash("Vault was deleted!")
                    return index_path(data_path[:splitter_index_dir_path])
        elif data_type != "folder" and data_type != "vault":#file
            splitter_index_dir_path = data_path.rindex("/")
            directory = get_dir_by_path(data_path[:splitter_index_dir_path])
            for file in directory.files:
                if str(data_path[splitter_index_dir_path+1:]) == str(file.file_name):
                    db.session.delete(file)
                    directory.file_count -= 1
                    db.session.commit()
                    flash("File was deleted!")
                    return index_path(data_path[:splitter_index_dir_path])
        else:#folder
            for directory in dirs:
                if str(data_path_enc) == str(directory.dir_path):
                    for file in directory.files:
                        db.session.delete(file)
                    for vault in directory.vaults:
                        db.session.delete(vault)
                    db.session.delete(directory)
                    db.session.commit()
                    remDirsRec(data_path)
                    flash("Folder" + (data_path[data_path.rindex("/"):])[:19] + "was deleted!")
                    return index_path(data_path[:data_path.rindex("/")])
        return redirect(url_for("index"))
    else:
        flash("Logout timer expired")
        return redirect(url_for("index"))

@app.route("/rename")
def rename():
    if current_user.is_authenticated:
        session_name = current_user.user_manager_id + current_user.username + current_user.get_id()
        dir_focused = request.args.get('path')
        new_field_name = request.args.get('new_name')
        data_type = request.args.get('type')
        if data_type == "folder":
            dir = get_dir_by_path(dir_focused)
            if dir != None:
                new_folder_name_enc = encrypt(new_field_name.encode(), session[session_name+"key"], session[session_name+"iv"])
                splitter_index_dir_path = dir_focused.rindex("/")
                if duplicates_folder(new_field_name, dir_focused[:splitter_index_dir_path]):
                    dir.dir_name = new_folder_name_enc

                    dir_path = decrypt(dir.dir_path.encode(), session[session_name+"key"], session[session_name+"iv"]).decode()

                    splitter_index_dir_path = dir_path.rindex("/")
                    new_dir_href = dir_path[:splitter_index_dir_path] + "/" + new_field_name
                    dir.dir_path = encrypt(new_dir_href.encode(), session[session_name+"key"], session[session_name+"iv"])
                    db.session.commit()
                    flash("Folder renamed to" + new_field_name[:19] + ".. !")

                else:
                    flash("Folder does already exists!")
        elif data_type == "vault":
            splitter_index_dir_path = dir_focused.rindex("/")
            dir = get_dir_by_path(dir_focused[:splitter_index_dir_path])
            if dir != None:
                print(dir_focused[splitter_index_dir_path:])
                vault = get_vault_by_name(dir_focused[splitter_index_dir_path+1:], dir)
                if vault != None:
                    new_enc_name = encrypt(new_field_name.encode(), session[session_name+"key"], session[session_name+"iv"])
                    if duplicates_vault(new_enc_name, dir_focused[:splitter_index_dir_path]):
                        vault.vault_name = new_enc_name
                        db.session.commit()
                        flash("Vault renamed to" + ".. !")
                    else:
                        flash("Vault does already exists!")
        elif data_type == "file":
            splitter_index_dir_path = dir_focused.rindex("/")
            dir = get_dir_by_path(dir_focused[:splitter_index_dir_path])
            if dir != None:
                print(dir_focused[splitter_index_dir_path+1:])
                file = get_file_from_dir(dir, dir_focused[splitter_index_dir_path+1:])
                if file != None:
                    new_enc_name = encrypt(new_field_name.encode(), session[session_name+"key"], session[session_name+"iv"])
                    if duplicates_file(new_enc_name, dir_focused[:splitter_index_dir_path]):
                        file.file_name = new_enc_name
                        db.session.commit()
                        flash("File renamed to " + new_field_name[:19] + ".. !")
                    else:
                        flash("File does already exists!")


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