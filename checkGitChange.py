import os
import subprocess

def checkStatus(path=None):
    if path:
        os.chdir(path)
    cmdList = ["git","status","-s"]
    output = subprocess.check_output(cmdList)
    statusList = output.decode().split("\n")
    fileNames, dirNames, symLinks = [], [], []

    for status in statusList:
        if len(status)>3:
            flags = status[:3]
            fileName = status[3:]
            if os.path.islink(fileName) or os.path.ismount(fileName): symLinks.append(fileName)
            elif os.path.isdir(fileName): dirNames.append(fileName)
            elif os.path.isfile(fileName): fileNames.append(fileName)
            else:
                print("NONEXISTANT OR UNKNOWN TYPE FILE:", fileName)
    return fileNames, dirNames, symLinks
    
if __name__ == "__main__":
    repoPath = "/root/Desktop/works/sync_git_repos/example"
    checkStatus(repoPath)