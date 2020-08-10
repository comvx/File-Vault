from flask_login import UserMixin

from Vault import login_manager, db

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_manager_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(), unique=True, nullable=False)
    master_password = db.Column(db.String(), nullable=False)
    manager = db.relationship('Manager', backref='author', lazy=True)

class Manager(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    dirs = db.relationship('Directory', backref='author', lazy=True)

class Directory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('manager.id'), nullable=False)
    dir_name = db.Column(db.String(), nullable=False, default="root")
    file_count = db.Column(db.Integer, nullable=False, default=0)
    files = db.relationship('File', backref='author', lazy=True)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    directory_id = db.Column(db.Integer, db.ForeignKey('directory.id'), nullable=False)
    file_name = db.Column(db.String(), nullable=False, default="defaul")
    file_ext = db.Column(db.String(), nullable=False, default=".defaut")
    file_id = db.Column(db.Integer, nullable=False, default=0)
    file_data = db.Column(db.String())