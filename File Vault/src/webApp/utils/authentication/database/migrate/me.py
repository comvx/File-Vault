from webApp.utils.authentication.database.table import User, vaults, files
from webApp.utils.authentication.database.migrate import dataset, table, db
import base64

def get_data():
    user = User.query.filter_by(user_manager_id="u-f9f05c1297e7e3937cb41ae7638e2c1c034c538ffc7dde951ae7d951c23a632cfa98ac02d066ca2cf34c58fb8c0378fc03f472e0a9b0457606a0fe0bebe4d632").first()
    new_user = table.User(user_manager_id=user.user_manager_id, username=user.username, master_password=user.master_password)
    db.session.add(new_user)
    for directory in user.directorys:
        new_dir = table.Directory(dir_name=directory.dir_name, file_count=directory.file_count, dir_path=directory.dir_path, user=new_user)
        db.session.add(new_dir)
        for file in directory.files:
            if file.file_share == False:
                new_file = table.File(file_name=file.file_name, file_ext=file.file_ext, file_data=file.file_data, file_share=file.file_share)
                new_dir.files.append(new_file)
        for vault in directory.vaults:
            if vault.vault_share == False:
                new_vault = table.Vault(vault_name=vault.vault_name, vault_username=vault.vault_username, vault_password=vault.vault_password, vault_share=vault.vault_share)
                new_dir.vaults.append(new_vault)
    db.create_all()        
    db.session.commit()