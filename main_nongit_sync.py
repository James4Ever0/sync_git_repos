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

autobackupPath = os.path.join(cwd,"autobackup.sh") # this one is shit. this could ruin everything. on macos only git sync is needed.



import threading

def startDaemonThread(target, args=(), kwargs={}):
    thread = threading.Thread(target=target, args=args, kwargs={}, daemon=True)
    thread.start()

def asyncDaemonThread(func):
    def new_func(*args, **kwargs):
        startDaemonThread(func, args=args, kwargs=kwargs)
    return new_func

running = False

@asyncDaemonThread
def task():
    global running
    print("RUNNING NON_GIT SYNC")
    if not running:
        running=True
        os.system("bash {}".format(autobackupPath)) # this is not init.
        running=False

    # also check if vscode is alive for this repo.
    # just check existance of a file.


schedule.every(1).hour.do(task)

import yaml

configPath = "{}/sync.yml".format(scriptBase)

with open(configPath, "r", encoding="utf-8") as f:
    monitoringDict = yaml.safe_load(f.read())

monitoringPaths = list(monitoringDict.keys())
# abspath: /media/root/help/pyjom
if not os.path.exists(autobackupPath):
    print("NO AUTOBACKUP SCRIPT EXISTS.")
    exit()

myUUID = None
init = True
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
        init = False
        task()
        continue
    schedule.run_pending()
    time.sleep(3)
