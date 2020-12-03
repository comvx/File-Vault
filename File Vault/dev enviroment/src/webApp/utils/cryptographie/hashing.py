import hashlib, binascii, os

def hash(input, iteration, salt):
    '''
    return string
    '''
    pwdHash = hashlib.pbkdf2_hmac("sha512", input.encode("utf-8"), salt, iteration)
    pwdHash = binascii.hexlify(pwdHash)
    return pwdHash.decode("ascii")

def check_password(user_hashed_pwd, input_pwd, iteration, salt):
    input_pwd_hash = hash(input_pwd, iteration, salt)
    if input_pwd_hash == user_hashed_pwd.decode():
        return True