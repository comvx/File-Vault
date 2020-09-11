class dataset():
    def __init__(self, pname, ptype, ppath, pdata, phref, penc_name, pchild_items):
        self.data_set = {
        "name" : pname,
        "type" : ptype,
        "path" : ppath,
        "data" : pdata,
        "href" : phref,
        "enc_name" : penc_name,
        "child_items" : pchild_items
        }
class vaultset():
    def __init__(self, pname, pusername, ppassword, pid):
        self.data_set = {
        "name" : pname,
        "username" : pusername,
        "password" : ppassword,
        "id" : pid
        }