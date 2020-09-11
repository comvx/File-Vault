#from Vault import app
from webApp.utils.authentication.creds import *
from webApp.utils.authentication.database.table import *
from webApp import app, db
from pathlib import Path
import shutil, os

if __name__ == '__main__':
    shutil.rmtree(str(os.getcwd()).replace('\\', "/") + "/webApp/utils/authentication/database/session_data/server-sided/")
    os.mkdir(str(os.getcwd()).replace('\\', "/") + "/webApp/utils/authentication/database/session_data/server-sided/")
    app.run(debug=True, host="192.168.178.88")
    #test = Credentials("comvx", "Kleffmann", "u-d1a333b5e445d84f217954992f2d529374611fb1d5575c402676fd81b139a37681f0178aec43da7851405249a554198ab442bd47709c3b580beae7d234af0221")
    #output = test.get_SecretKey()
    #print(output)
