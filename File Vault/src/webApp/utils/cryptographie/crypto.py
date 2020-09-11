from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import base64

def pad(s):
    padding = algorithms.AES.block_size - len(s) % algorithms.AES.block_size 
    return s + bytes([padding]) * padding

def _unpad(s):
    return s[:-s[-1]]

def encrypt(data, key, IV):
    backend = default_backend()
    digest = hashes.Hash(hashes.SHA256(), backend=backend)
    digest.update(key.encode())
    key = digest.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(IV), backend=backend)
    encryptor = cipher.encryptor()
    data = pad(data)

    output = encryptor.update(data) + encryptor.finalize()
    return base64.b16encode(output)

def decrypt(data, key, IV):
    backend = default_backend()
    data = base64.b16decode(data)
    digest = hashes.Hash(hashes.SHA256(), backend=backend)
    digest.update(key.encode())
    key = digest.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(IV), backend=backend)
    decryptor = cipher.decryptor()
    return  _unpad(decryptor.update(data))