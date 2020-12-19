#from Crypto import Random
#from Crypto.Cipher import AES
#from Crypto.Hash import SHA256
import random
import os
import hashlib
import string
import secrets
import base64

from binascii import hexlify

from webApp.utils.cryptographie.hashing import hash
from webApp.utils.data import pad

gen = secrets.SystemRandom()

def gen_String(s, e):
    return hexlify(os.urandom(gen.randint(s, e))).decode()

def gen_Pass():
    chars = string.ascii_letters + string.digits + "!?()_"
    return "".join(secrets.choice(chars) for i in range(gen.randint(20, 30)))

def gen_Number():
    return gen.randint(20, 35)

def gen_user_id(username):
    return "u-" + hash(username, (len(username)*len(username))*round((len(username)/2)), pad(username, 64).encode())

def gen_vault_key(iv, iter, username):
    return hash(gen_Pass(len(username) * len(username)), iter, salt)

def gen_secret_key(iv, salt):
    return base64.b64encode(iv.decode()+salt.decode()).decode()