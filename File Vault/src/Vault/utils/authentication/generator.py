#from Crypto import Random
#from Crypto.Cipher import AES
#from Crypto.Hash import SHA256
import random
import os
import hashlib
import string
import secrets

from binascii import hexlify

from Vault.utils.cryptographie.hashing import hash
from Vault.utils.data import pad

gen = secrets.SystemRandom()

#def gen_IV():
#    return Random.new().read(AES.block_size)

def gen_String():
    return hexlify(os.urandom(gen.randint(99, 200)))

#def gen_salt():
#    return hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")

def gen_Pass(max):
    chars = string.ascii_letters + string.digits + "!?()_"
    return "".join(secrets.choice(chars) for i in range(gen.randint(30, max)))

def gen_Number():
    return gen.randint(20, 35)

def gen_user_id(username):
    print(len(pad(username, 64)))
    return "u-" + hash(username, (len(username)**len(username))*round((len(username)/2)), pad(username, 64).encode())

def gen_vault_key(iv, iter, username):
    return hash(gen_Pass(len(username) * len(username)), iter, salt)