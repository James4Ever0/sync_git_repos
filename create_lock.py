import os
import pathlib

cwd = os.curdir
cwd = os.path.abspath(cwd)

scriptBase = os.path.abspath(__file__)
scriptBase = os.path.dirname(scriptBase)
# print(cwd)
lock_name = cwd.replace("/", "_") + ".lock"
lock_path = os.path.join("{}/locks".format(scriptBase), lock_name)

import yaml

configPath = "{}/sync.yml".format(scriptBase)

with open(configPath, "r", encoding="utf-8") as f:
    monitoringDict = yaml.safe_load(f.read())

monitoringPaths = list(monitoringDict.keys())
# abspath: /media/root/help/pyjom
import uuid


import subprocess


def getActiveVscodeWorkingDirs():
    scriptPath = os.path.join(scriptBase, "getActiveVscodeWorkingDirs.sh")
    cmdList = ["bash", scriptPath]
    output = subprocess.check_output(cmdList)
    output = output.decode().split("\n")
    output = [x.replace("\n", "") for x in output if len(x) > 2]
    return output

sessionName = "double_sync" + cwd.replace("/", "_")

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

if cwd in monitoringPaths:
    if (
        (cwd not in getActiveVscodeWorkingDirs())
        and (sessionName not in getRunningTmuxSessionNames())
    ) or (
        not os.path.exists(lock_path)
    ):  # ensure no shit happens?
        pathlib.Path(lock_path).touch()
        with open(lock_path, "w+") as f:
            f.write(str(uuid.uuid4()))
