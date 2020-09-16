#from Vault import app
from webApp.utils.authentication.creds import *
from webApp.utils.authentication.database.table import *
from webApp import app, db
from pathlib import Path
import shutil, os

if __name__ == '__main__':
    shutil.rmtree(str(os.getcwd()).replace('\\', "/") + "/webApp/utils/authentication/database/session_data/server-sided/")
    os.mkdir(str(os.getcwd()).replace('\\', "/") + "/webApp/utils/authentication/database/session_data/server-sided/")
    app.run(debug=True)
