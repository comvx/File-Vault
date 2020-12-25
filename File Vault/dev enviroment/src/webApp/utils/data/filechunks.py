import json
import os

from webApp.utils.cryptographie import decomp, comp
from webApp.utils.cryptographie import decrypt

class Chunks():
    def __init__(self, config):
        if(os.path.exists(config.path.replace("/"+config.name+".json", "")) == False):
            os.mkdir(config.path.replace("/"+config.name+".json", ""))
        if(os.path.exists(config.path)):
            data = ""
            with open(config.path, "r") as handler:
                data = handler.read()
            self.json_chunks = json.loads(data)
        else:
            self.json_chunks = {}

    def addChunk(self, index, data):
        self.json_chunks[str(index)] = comp(data.encode())
    
    def sortChunks(self):
        sorted = {}
        keys = self.json_chunks.keys()
        for i in range(len(keys)):
            value = self.getValueByKey(str(i))
            sorted[str(i)] = value
        del self.json_chunks
        self.json_chunks = sorted

    def getValueByKey(self, key):
        return self.json_chunks[key]

    def getFileFDB(self, session_name, session):
        data = None
        for chunk in self.json_chunks.values():
            dec_chunk = self.decChunk(session_name, session, chunk)
            if(data == None):
                data = dec_chunk
            else:
                data = data+dec_chunk
        return data
    def decChunk(self, session_name, session, chunk):
        return decrypt(decomp(chunk).decode(), session[session_name+"key"], session[session_name+"iv"])

    def saveJson(self, config):
        with open(config.path, "w") as handler:
            json.dump(self.json_chunks, handler)