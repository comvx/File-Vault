class User():
    def __init__(self, user_manager_id, username, master_password, directorys, shares):
        self.data_set = {
        "user_manager_id" : user_manager_id,
        "username" : username,
        "master_password" : master_password,
        "directorys" : directorys,
        "shares" : shares
        }
class Share():
    def __init__(self, user_id, uuid, href):
        self.data_set = {
        "user_id" : user_id,
        "uuid" : uuid,
        "href" : href
        }
class Directory():
    def __init__(self, user_id, dir_name, file_count, dir_path, files, vaults):
        self.data_set = {
        "user_id" : user_id,
        "dir_name" : dir_name,
        "file_count" : file_count,
        "dir_path" : dir_path,
        "files" : files,
        "vaults" : vaults
        }
class File():
    def __init__(self, file_name, file_ext, file_data, file_share):
        self.data_set = {
        "file_name" : file_name,
        "file_ext" : file_ext,
        "file_data" : file_data,
        "file_share" : file_share
        }
class Vault():
    def __init__(self, vault_name, vault_username, vault_password, vault_share):
        self.data_set = {
        "vault_name" : vault_name,
        "vault_username" : vault_username,
        "vault_password" : vault_password,
        "vault_share" : vault_share
        }