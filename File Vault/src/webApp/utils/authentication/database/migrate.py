from webApp.utils.authentication.database.table import User
from webApp.utils.authentication.database.migrate import dataset, table, db


def migrate():
    users = User.query.all()
    shares = list()
    for user in users:
        new_user = table.User(user_manager_id=user.user_manager_id, username=user.username, master_password=user.master_password)
        db.session.add(new_user)
        for share in user.shares:
            new_share = table.Share(uuid=share.uuid, href=share.href, user=new_user)
            db.session.add(new_share)
        for directory in user.directorys:
            new_dir = table.Directory(dir_name=directory.dir_name, file_count=directory.file_count, dir_path=directory.dir_path, user=new_user)
            db.session.add(new_dir)
            for file in directory.files:
                new_file = table.File(file_name=file.file_name, file_ext=file.file_ext, file_data=file.file_data, file_share=file.file_share)
                db.session.add(new_file)
            for vault in directory.vaults:
                new_vault = table.Vault(vault_name=vault.vault_name, vault_username=vault.vault_username, vault_password=vault.vault_password, vault_share=vault.vault_share)
                db.session.add(new_vault)
        db.create_all()        
        db.session.commit()
                
            


    