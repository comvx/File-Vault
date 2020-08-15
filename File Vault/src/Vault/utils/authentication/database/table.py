from flask_login import UserMixin

from Vault import login_manager, db

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

files = db.Table('directory_files', db.Column('file_id', db.Integer, db.ForeignKey('file.id')), db.Column('directory_id', db.Integer, db.ForeignKey('directory.id')))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    user_manager_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(), unique=True, nullable=False)
    master_password = db.Column(db.String(), nullable=False)
    directorys = db.relationship('Directory', backref='user')

class Directory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    dir_name = db.Column(db.String(), nullable=False, default="root")
    file_count = db.Column(db.Integer, default=0)
    dir_path = db.Column(db.String(), nullable=False, default="/")
    
    files = db.relationship('File', secondary=files, backref='directory')

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    file_name = db.Column(db.String(), nullable=False, default="defaul")
    file_ext = db.Column(db.String(), nullable=False, default=".defaut")
    file_data = db.Column(db.String())