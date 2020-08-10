#from Vault import app
from Vault.utils.authentication.creds import *
from Vault.utils.authentication.database.table import *
from Vault import app, db
from pathlib import Path
import shutil, os

if __name__ == '__main__':
    shutil.rmtree(str(os.getcwd()).replace('\\', "/") + "/Vault/utils/authentication/database/session_data/server-sided/")
    os.mkdir(str(os.getcwd()).replace('\\', "/") + "/Vault/utils/authentication/database/session_data/server-sided/")
    app.run(debug=True, host="127.0.0.1")
    #test = Credentials("comvx", "f12", "u-728173817238")
    #output = test.get_SecretKey()
    #print(output)
