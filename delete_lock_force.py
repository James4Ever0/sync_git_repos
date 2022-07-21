import os

scriptBase = os.path.abspath(__file__)
scriptBase = os.path.dirname(scriptBase)

cwd = os.curdir
cwd = os.path.abspath(cwd)

lock_name = cwd.replace("/","_")+".lock"
lock_path = os.path.join("{}/locks".format(scriptBase),lock_name)

if os.path.exists(lock_path):
    os.remove(lock_path)