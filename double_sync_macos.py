# import schedule
# import time
import os

cwd = os.curdir
cwd = os.path.abspath(cwd)

scriptBase = os.path.abspath(__file__)
scriptBase = os.path.dirname(scriptBase)

lockBase = os.path.join(scriptBase, 'locks')
if not os.path.exists(lockBase): os.mkdir(lockBase)

os.system("rm -rf {}/double_sync_macos.yml".format(scriptBase))
# print(cwd)
lock_name = cwd.replace("/", "_") + ".lock"
lock_path = os.path.join("{}/locks".format(scriptBase), lock_name)

import yaml

configPath = "{}/sync.yml".format(scriptBase)

with open(configPath, "r", encoding="utf-8") as f:
    monitoringDict = yaml.safe_load(f.read())

monitoringPaths = list(monitoringDict.keys())

import jinja2

tmuxpTemplate = os.path.join(scriptBase, "double_sync_macos.yml.j2")
with open(tmuxpTemplate, "r") as f:
    tmuxpTemplate = jinja2.Template(f.read())
tmuxpScript = os.path.join(scriptBase, "double_sync_macos.yml")

import subprocess


def getActiveVscodeWorkingDirs():
    scriptPath = os.path.join(scriptBase, "getActiveVscodeWorkingDirsMacOS.sh")
    # scriptPath = os.path.join(scriptBase, "getActiveVscodeWorkingDirs.sh")
    cmdList = ["bash", scriptPath, scriptBase]
    output = subprocess.check_output(cmdList)
    output = output.decode().split("\n")
    output = [x.replace("\n", "") for x in output if len(x) > 2]
    return output


import libtmux

server = libtmux.Server()


def getRunningTmuxSessionNames():
    try:
        sessions = server.list_sessions()
    except:
        sessions = []
    session_names = []
    for session in sessions:
        try:
            session_name = session["session_name"]
            session_names.append(session_name)
        except:
            pass
    return session_names


import time

sessionName = "double_sync" + cwd.replace("/", "_")

lock_name = cwd.replace("/", "_") + ".lock"
lock_path = os.path.join("{}/locks".format(scriptBase), lock_name)

def checkAttached():
    try:
        for session in server.list_sessions():
            if session["session_name"] == sessionName:
                attached = session["session_attached"]
                print("ATTACHED?",attached)
                # no need to attach this shit though.
                if attached == "0":
                    print("SYNC SESSION {} NOT ATTACHED".format(sessionName))
                    # os.system("tmux attach -t -d {}".format(sessionName))
    except:pass
if (sessionName in getRunningTmuxSessionNames()) and (os.path.exists(lock_path)):
    print("CURRENTLY HAS OTHER SYNC PROCESS WORKING HERE")
    print("WILL NOT LAUNCH NEW SYNC PROCESS")
    # attached?
    checkAttached()
    exit()

if cwd in monitoringPaths:
    # if os.path.exists(lock_path):# must not exist here.
    print("SYNCING DIR", cwd)
    # os.system("tmux kill-session -t double_sync") # brutal. change this shit.
    while True:
        tmuxSessionNames = getRunningTmuxSessionNames()
        if sessionName in tmuxSessionNames:
            print("WAITING FOR PREVIOUS {} session to exit.".format(sessionName))
            time.sleep(3)
        else:
            break
    # if os.path.exists()
    os.system("python3 {}/create_lock_macos.py".format(scriptBase))
    with open(tmuxpScript, "w+") as f:
        f.write(
            tmuxpTemplate.render(sessionName=sessionName, scriptBase=scriptBase)
        )
    os.system("tmuxp load -y -d {}".format(tmuxpScript)) # must be running otherwise no shit will launch.
    # checkAttached()
else:
    print("Not in monitoring paths")