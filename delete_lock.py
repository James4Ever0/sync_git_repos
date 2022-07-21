import os
import subprocess

scriptBase = os.path.abspath(__file__)
scriptBase = os.path.dirname(scriptBase)

def getActiveVscodeWorkingDirs():
    scriptPath = os.path.join(scriptBase,"getActiveVscodeWorkingDirs.sh")
    cmdList = ["bash", scriptPath]
    output = subprocess.check_output(cmdList)
    output = output.decode().split("\n")
    output = [x.replace("\n","") for x in output if len(x)>2]
    return output


cwd = os.curdir
cwd = os.path.abspath(cwd)
# print(cwd)
lock_name = cwd.replace("/","_")+".lock"
lock_path = os.path.join("{}/locks".format(scriptBase),lock_name)

import yaml

configPath = "{}/sync.yml".format(scriptBase)

with open(configPath, "r", encoding="utf-8") as f:
    monitoringDict = yaml.safe_load(f.read())

monitoringPaths = list(monitoringDict.keys())
# abspath: /media/root/help/pyjom

import time
init = True
while True:
    if init:
        time.sleep(10)
        init=False
    else:
        time.sleep(1)
    vscodeWDs = getActiveVscodeWorkingDirs()
    if cwd not in vscodeWDs or cwd not in monitoringPaths:
        if os.path.exists(lock_path):
            os.remove(lock_path)
        break
# print(scriptBase)