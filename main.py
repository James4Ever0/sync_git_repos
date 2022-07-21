import schedule
import time
import os

cwd = os.curdir
cwd = os.path.abspath(cwd)

scriptBase = os.path.abspath(__file__)
scriptBase = os.path.dirname(scriptBase)

# print(cwd)
lock_name = cwd.replace("/", "_") + ".lock"
lock_path = os.path.join("{}/locks".format(scriptBase), lock_name)


def task():
    # cannot make it into a daemon thread since that will definitely break consistency of git repo.
    os.system("python3 {}/sync_logic.py".format(scriptBase)) # this is not init.
    # also check if vscode is alive for this repo.
    # just check existance of a file.


schedule.every(15).seconds.do(task)

import yaml

configPath = "{}/sync.yml".format(scriptBase)

with open(configPath, "r", encoding="utf-8") as f:
    monitoringDict = yaml.safe_load(f.read())

monitoringPaths = list(monitoringDict.keys())
# abspath: /media/root/help/pyjom

myUUID = None
init=True
while True:
    if cwd not in monitoringPaths:
        print("NOT IN MONITORING PATH LIST")
        break
    if not os.path.exists(lock_path):
        print("LOCK HAS GONE. VSCODE HAS EXITED.")
        break
    else:
        with open(lock_path, "r") as f:
            myCode = f.read()
        if myUUID is None: myUUID = myCode
        else:
            if myUUID != myCode:
                print("UUID CHANGED. MAIN VSCODE SESSION HAS CHANGED!")
                break
    if init:
        init=False
        task()
        continue
    schedule.run_pending()
    time.sleep(3)
