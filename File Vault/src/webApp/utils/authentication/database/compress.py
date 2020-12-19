from webApp.utils.cryptographie import comp, decomp
from webApp import *

import base64

def compress():
    users = User.query.all()
    for user in users:
        for directory in user.directorys:
            for file in directory.files:
                file.file_data = comp(base64.b16decode(file.file_data))
                file.file_name = comp(base64.b16decode(file.file_name))
                file.file_ext = comp(base64.b16decode(file.file_ext))
                db.session.commit()
            for vault in directory.vaults:
                vault.vault_name = comp(base64.b16decode(vault.vault_name))
                vault.vault_username = comp(base64.b16decode(vault.vault_username))
                vault.vault_password = comp(base64.b16decode(vault.vault_password))

def decompress():
    users = User.query.all()
    for user in users:
        for directory in user.directorys:
            for file in directory.files:
                file.file_data = decomp(base64.b64decode(file.file_data)).decode()
                db.session.commit()