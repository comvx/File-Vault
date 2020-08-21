from Vault.utils.cryptographie import *

class Credentials:
    vault_masterpassword = None
    vault_username = None
    user_id = None
    len_vault_username = None
    len_vault_masterpassword = None
    #
    len_user_id_hashed = None
    user_id_hash = None

    #user_id={lenght=fixed(64)}
    def __init__(self, pvault_username, pvault_masterpassword, puser_id):
        self.user_id = puser_id
        self.vault_username = hash(pvault_username, 99999, puser_id.encode())
        self.vault_masterpassword = hash(pvault_masterpassword, 98765, puser_id.encode())
        self.len_vault_username = len(pvault_username)
        self.len_vault_masterpassword = len(pvault_masterpassword)
        self.len_user_id = len(self.user_id)
        self.user_id_hash = hash(self.user_id, 14082, puser_id.encode())

    def get_creds(self, obj_1, obj_2, const, merged_data):
        output = None 
        if obj_1 > obj_2:
            calc_value = const - (obj_1 - obj_2)
            if calc_value < 0:
                self.mani_value = obj_1 - calc_value
            else:
                self.mani_value = obj_1 + calc_value
            output = merged_data[obj_2:self.mani_value]

        elif obj_1 < obj_2:
            calc_value = const - (obj_2 - obj_1)
            if calc_value < 0:
                self.mani_value = obj_2 - calc_value
            else:
                self.mani_value = obj_2 + calc_value
            output = merged_data[obj_1:self.mani_value]
        else:
            calc_value = const - (obj_2)
            if calc_value < 0:
                self.mani_value = obj_2 - calc_value
            else:
                self.mani_value = obj_2 + calc_value
            output = merged_data[obj_1:self.mani_value]

        return output
        #IV = 16
        #SALT = 64

    def get_SecretKey(self): #1 start
        #obj_1=master_password length
        #obj_2=username length
        merged_data_salt = hash((self.vault_username+self.vault_masterpassword+self.user_id_hash)*(self.len_vault_masterpassword+self.len_vault_username), 99999, self.user_id.encode())
        salt = self.get_creds(self.len_vault_masterpassword, self.len_vault_username, 64, merged_data_salt).encode()
        merged_data_iv = hash((self.vault_username+self.vault_masterpassword)*(self.len_vault_masterpassword+self.len_vault_username), 99999, salt)
        iv = self.get_creds(self.len_vault_masterpassword, self.len_vault_username, 16, merged_data_iv).encode()
        return iv+salt

    def gen_UserKey(self, salt): #2 start
        hash_list = hash(self.vault_username, 10000, salt), hash(self.vault_masterpassword, 10000, salt), hash(self.user_id, 10000, salt)
        user_pass_hash = hash(hash_list[1] + hash_list[2], 50000, salt)
        pass_id_hash = hash(hash_list[2] + hash_list[0], 50000, salt)
        userKey = hash(user_pass_hash + pass_id_hash, len(self.vault_username) * len(self.vault_masterpassword), salt)
        return userKey

    def gen_key(self, psecret_key, salt):#3 start
        secret_key = hash(psecret_key.decode("ascii"), 99999, salt)
        key = hash(secret_key + self.gen_UserKey(salt), 99999, salt)
        return key