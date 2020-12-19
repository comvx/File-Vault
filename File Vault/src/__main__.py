#from Vault import app
from webApp.utils.authentication.creds import *
from webApp.utils.authentication.database.table import *
from webApp.utils.authentication.database.compress import *
from webApp.utils.authentication.database.migrate.me import *
from webApp.utils.authentication.database.migrate.migrate import *
from webApp import app, db
from pathlib import Path
import shutil, os
from webApp.utils.authentication.generator import gen_user_id, gen_Pass, gen_String

if __name__ == '__main__':
    #get_data()
    app.run(debug=True, host="192.168.178.88")
    #print(gen_user_id(""))
    #compress()
    #migrate()
