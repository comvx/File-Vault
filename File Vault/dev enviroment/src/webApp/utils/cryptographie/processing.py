from zlib import compress, decompress
import base64

def comp(data):#data = bytes
    return base64.b16encode(compress(data, 3)).decode()

def decomp(data):#data = string
    return decompress(base64.b16decode(data))