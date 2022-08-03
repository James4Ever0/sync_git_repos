# what is the current working directory?

import os
import argparse
# from tempfile import TemporaryDirectory  # have init logic.
import yaml
# import filelock
import shutil

# from configs import *
import git
import time
import subprocess
import re

scriptBase = os.path.abspath(__file__)
scriptBase = os.path.dirname(scriptBase)

# temporaryDirectory = "/dev/shm"
temporaryDirectory = "/tmp"

# change to new key path.
ssh_keyPath = "/Users/jamesbrown/.notable/id_rsa_original_backup"
# ssh_keyPath = "/root/Desktop/works/notes_ssh_keys/id_rsa_original_backup"

def checkStatus(path=None):
    if path:
        os.chdir(path)
    cmdList = ["git", "status", "-s"]
    output = subprocess.check_output(cmdList)
    statusList = output.decode().split("\n")
    fileNames, dirNames, symLinks = [], [], []

    for status in statusList:
        if len(status) > 3:
            flags = status[:3]
            fileName = status[3:]
            if os.path.islink(fileName) or os.path.ismount(fileName):
                symLinks.append(fileName)
            elif os.path.isdir(fileName):
                dirNames.append(fileName)
            elif os.path.isfile(fileName):
                fileNames.append(fileName)
            else:
                print("NONEXISTANT OR UNKNOWN TYPE FILE:", fileName)
    return fileNames, dirNames, symLinks


configPath = "{}/sync.yml".format(scriptBase)


with open(configPath, "r", encoding="utf-8") as f:
    monitoringDict = yaml.safe_load(f.read())

monitoringPaths = list(monitoringDict.keys())
# abspath: /media/root/help/pyjom
# so no freaking symlink avaliable.
parser = argparse.ArgumentParser()
parser.add_argument(
    "-i",
    "--init",
    help="initialize monitored directory as git repo and create a custom .gitignore file, pass target remote git url here.",
    default="",
    type=str,
)  # during initialization you may want to ignore all .git paths or include subgit repos.


parser.add_argument(
    "-b",
    "--branch",
    help="the branch to be commited to",
    default="main",
    type=str,
)  # during initialization you may want to ignore all .git paths or include subgit repos.

args = parser.parse_args()
init = args.init
commit_branch = args.branch
# print("INIT",init)

absPath = os.path.abspath(os.curdir)
submodule_remote_backup_path = "submodules.yml"
submodule_remote_backup_path = os.path.join(absPath, submodule_remote_backup_path)
# /root/Desktop/works/sync_git_repos/sync_logic.py
print("ABSOLUTE WORKING DIRECTORY:", absPath)


def removePath(path):
    assert os.path.isabs(path)
    # os.system("rm -rf %s" % path)
    shutil.rmtree(path)


filesize_limit = 100  # 100 KB per file max for selected file types. this is a private repo so we should not share it with any other ones.

print(monitoringPaths)

allowSuffix = [
    ".py",
    ".js",
    ".mjs",
    ".mts",
    ".ts",
    ".map",
    ".info",
    ".markdown",
    ".c",
    ".h",
    ".cpp",
    ".hpp",
    ".go",
    ".lua",
    ".yml",
    ".yaml",
    ".json",
    ".mjson",
    ".mdl",
    ".j2",
    ".html",
    ".md",
    ".txt",
    ".rst",
    ".log",
    ".sh",
    ".cmd",
    ".ps1",
    ".xsh",
    ".xonsh",
]


allowFileName = ["readme", ".gitignore", ".subModuleOrigin"]  # lowers.

addGlob = " ".join(
    ["*{}".format(x) for x in allowSuffix]
    + ["*/{}".format(x) for x in allowFileName]
    + ["*/*/{}".format(x) for x in allowFileName]
    + ["{}".format(x) for x in allowFileName]
)


def checkAllowedFile(fileName):
    fileNameLower = fileName.lower()
    for suffix in allowSuffix:
        if fileNameLower.endswith(suffix.lower()):
            return True
    for allowName in allowFileName:
        if fileNameLower == allowName.lower():
            return True
    return False


# shell scripts
import progressbar

# from sync_logic import checkStatus
gitIgnoreData = []  # all globs
gitIgnoreFileNameData = []
gitIgnorePath = os.path.join(absPath, ".gitignore")

if init == "":
    with open(gitIgnorePath, "r") as f_read:
        data = f_read.read().replace("\r", "")
        data = data.split("\n")
        gitIgnoreData = [x.replace("\n", "") for x in data if len(x) > 3]
        gitIgnoreData = [x for x in gitIgnoreData if x.startswith("*")]
        gitIgnoreFileNameData = [x for x in gitIgnoreData if not x.startswith("*")]


def processReport(report, init=False, init_url="", changeLog=""):
    toDelete = report["delete"]  # must be git repos.
    toIgnore = report["ignore"]
    toIgnoreSuffix = report["ignoreSuffix"]  # must be a set.
    toIgnoreFileName = report["ignoreFileName"]  # must be a set.
    for elem in toDelete+toIgnoreSuffix+toIgnoreFileName:
        elemRelativePath = os.path.relpath(elem)
        os.system("git rm -r --cached {}".format(elemRelativePath))
    for elem in toDelete:
        try:
            repo = git.Repo(elem)
            working_dir = repo.working_dir
            relativeWorkingDir = os.path.relpath(working_dir)
            if working_dir != absPath:
                os.system("git rm -r {}".format(relativeWorkingDir)) # changed.
                # print(elem)
                try:
                    remoteUrls = [x for x in repo.remote().urls]
                    remoteUrl = remoteUrls[0]
                    if type(remoteUrl) == str and len(remoteUrl) > 5:
                        writePath = os.path.join(working_dir, ".subModuleOrigin")
                        with open(writePath, "w+") as f:
                            f.write(remoteUrl)
                except:
                    import traceback

                    traceback.print_exc()
                    breakpoint()
        except:
            import traceback

            traceback.print_exc()
            breakpoint()
            # now remove the .git thing.
        if elem.endswith(".git") and elem != os.path.join(absPath, ".git"):
            os.system("git rm -r {}".format(elem)) # changed.

    def writeGitIgnore(f_write, toIgnore, toIgnoreSuffix, toIgnoreFileName):
        for elem in toIgnore + toIgnoreFileName:
            elemAbsPath = os.path.abspath(elem)
            elemAbsParentDir = os.path.dirname(elemAbsPath)
            elemRelativePath = os.path.relpath(elem)
            elemFileName = os.path.basename(elemRelativePath)
            localGitIgnorePath = os.path.join(elemAbsParentDir, ".gitignore")
            # breakpoint()
            if os.path.exists(localGitIgnorePath):
                with open(localGitIgnorePath, "r+") as f_write_local:
                    localGitIgnoreList = [
                        x.replace("\n", "")
                        for x in f_write_local.read().replace("\r", "").split("\n")
                    ]
                    localGitIgnoreList = [x for x in localGitIgnoreList if len(x) > 0]
            else:
                localGitIgnoreList = []
            with open(localGitIgnorePath, "a+") as f_write_local:
                if elemFileName not in localGitIgnoreList:
                    f_write_local.write(
                        elemFileName.replace("[", "\\[")
                        .replace("]", "\\]")
                        .replace("*", "\\*")
                        .replace("(", "\\(")
                        .replace(")", "\\)")
                        + "\n"
                    )
        for elem in toIgnoreSuffix:
            f_write.write(elem + "\n")
        # for elem in toIgnoreFileName:
        #     f_write.write(elem + "\n")

    # write ignore file according to template.
    if init:
        with open(gitIgnoreTemplatePath, "r") as f_read:
            with open(gitIgnorePath, "w+") as f_write:
                f_write.write(f_read.read() + "\n")
                writeGitIgnore(f_write, toIgnore, toIgnoreSuffix, toIgnoreFileName)

    else:
        with open(gitIgnorePath, "a+") as f_write:
            # breakpoint()
            writeGitIgnore(f_write, toIgnore, toIgnoreSuffix, toIgnoreFileName)

    # init git repo.
    if init:
        commands = [
            "git init",
            "git add .",  # do not execute before we create/append the .gitignore file.
            "git commit -m 'first commit'",
            "git branch -M '{}'".format(commit_branch),
            "git remote add origin {}".format(init_url),
            "env GIT_SSH_COMMAND='ssh -i {}'  git push -f -u origin '{}'".format(ssh_keyPath,
                commit_branch
            ),  # force push.
        ]
    else:
        changeLog = (
            changeLog
            + "DELETE:\n{}\n\nIGNORE DIR:\n{}\n\nIGNORE FILE GLOB:\n{}\n\nIGNORE FILEPATH:\n{}".format(
                "\n".join(toDelete),
                "\n".join(toIgnore),
                "\n".join(toIgnoreSuffix),
                "\n".join(toIgnoreFileName),
            )
        )
        commit_message = "[{}]\n\n{}".format(
            time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), changeLog
        )
        # commit_message = re.escape(commit_message)
        commit_messagefile = "{}/commitMsg{}".format(temporaryDirectory,absPath.replace("/","_")) # this does not exist in macos. use /tmp instead?
        with open(commit_messagefile, "w+") as f:
            f.write(commit_message)
        commands = [ # git config pull.rebase true
            "git pull -f origin {}".format(commit_branch),
            "rm -rf .git/index.lock", # eliminate commit problems, rm not to prefix with git!
            "git add .",  # abandon addGlob
            "git commit -F {}".format(commit_messagefile),
            "git branch -M '{}'".format(commit_branch),
            "env GIT_SSH_COMMAND='ssh -i {}'  git push -u origin '{}'".format(ssh_keyPath,
                commit_branch
            ),
        ]
    # you could test the non-init update here, like checking the untracked submodule.
    # breakpoint()

    for command in commands:
        if init:
            print("EXECUTING INIT COMMAND")
        else:
            print("EXECUTING COMMAND")
        print(command)
        os.system(command)


def scanFiles(baseDir, fileName, report, sizeLimit):
    filePath = os.path.join(baseDir, fileName)
    fileName = os.path.basename(os.path.relpath(filePath))
    ###############GLOB MAGIC###############
    fileSuffix = None
    fileSuffixGlob = None
    if "." in fileName:
        if fileName[0] != "." or fileName.count(".") > 1:
            try:
                fileSuffix = fileName.split(".")[-1]
                assert fileSuffix != "."
                assert fileSuffix != ""
                fileSuffix = "." + fileSuffix
                fileSuffixGlob = "*" + fileSuffix  # no escape
                # fileSuffixGlob = "*" + re.escape(fileSuffix)
                if (fileSuffixGlob in gitIgnoreData) or (fileSuffix in allowSuffix):
                    fileSuffix = None
                    fileSuffixGlob = None
            except:
                fileSuffix = None
                fileSuffixGlob = None
    # else:
    breakflag = False
    # if fileName in ["redPacketLog_1.log", "redPacketLog_0.log"]:
    #     breakflag = True
    flag1 = os.path.islink(filePath) or os.path.ismount(filePath)
    # flag2 = not checkAllowedFile(fileName)
    flag2 = False  # just skip this shit.
    flag3 = os.path.getsize(filePath) > sizeLimit
    if flag1 or flag2 or flag3:
        if breakflag:
            print("FLAGS:", flag1, flag2, flag3)
            breakpoint()
        if fileSuffix is not None:
            if fileSuffixGlob not in report["ignoreSuffix"]:
                report["ignoreSuffix"].append(fileSuffixGlob)
        else:
            skipFlag = False
            for elem in report["ignore"]:
                if filePath.startswith(elem):
                    skipFlag = True
                    break
            if not skipFlag:
                report["ignoreFileName"].append(filePath)
        if breakflag:
            print(report["ignoreFileName"], filePath, fileName)
            breakpoint()
    return report


def scanDirs(baseDir, dirName, report):
    dirPath = os.path.join(baseDir, dirName)
    dirName = os.path.basename(os.path.relpath(dirPath))
    # if dirName == ".git" and not (os.path.islink(dirPath)): # now we choose the better way.
    #     report["delete"].append(dirPath)
    try:
        mRepo = git.Repo(dirPath)
        mWork = mRepo.working_dir
        mWork = os.path.abspath(mWork)
    except:
        mWork = absPath
    if dirName == ".git" and not (os.path.islink(dirPath)):
        try:
            repo = git.Repo(dirPath)
            work = repo.working_dir
            work = os.path.abspath(work)

            skipFlag = False
            for elem in report["ignore"]:
                if work.startswith(elem):
                    skipFlag = True
                    break
            if not skipFlag:
                report["ignore"].append(work)
        except:
            report["delete"].append(dirPath)
        # ignore all submodule folders. do not upload these things. only keep them on kali.
    elif os.path.islink(dirPath) or os.path.ismount(dirPath) or mWork != absPath:
        skipFlag = False
        for elem in report["ignore"]:
            if dirPath.startswith(elem):
                skipFlag = True
                break
        if not skipFlag:
            report["ignore"].append(dirPath)
    return report


def scanSymLinks(baseDir, symLink, report):
    symLinkPath = os.path.join(baseDir, symLink)
    symLink = os.path.basename(os.path.relpath(symLinkPath))

    skipFlag = False
    for elem in report["ignore"]:
        if symLinkPath.startswith(elem):
            skipFlag = True
            break
    if not skipFlag:
        report["ignore"].append(symLinkPath)
    return report


def scanPath(mPath, sizeLimit=1000 * 100):  # 100 KB limit?
    report = {
        "delete": [],
        "ignore": [],
        "ignoreSuffix": [],
        "ignoreFileName": [],
    }  # all absolute paths. convert to relative path first (without './' prefix)
    for baseDir, folders, files in progressbar.progressbar(os.walk(mPath)):
        if baseDir == absPath:
            continue
        ###############GLOB MAGIC###############
        for dirName in folders:
            report = scanDirs(baseDir, dirName, report)
        for fileName in files:
            report = scanFiles(baseDir, fileName, report, sizeLimit)
    return report
    # print("SCANNING")
    # print(elem)


def getStatusReport(fileNames, dirNames, symLinks, sizeLimit=1000 * 100):
    baseDir = absPath
    report = {
        "delete": [],
        "ignore": [],
        "ignoreSuffix": [],
        "ignoreFileName": [],
    }  # all absolute paths. convert to relative path first (without './' prefix)

    ###############GLOB MAGIC###############
    for symLink in symLinks:
        report = scanSymLinks(baseDir, symLink, report)
    for dirName in dirNames:
        report = scanDirs(baseDir, dirName, report)
        # report["ignore"].append(symLinkPath)
    for fileName in fileNames:
        report = scanFiles(baseDir, fileName, report, sizeLimit)
    return report


if absPath in monitoringPaths:
    gitIgnoreTemplatePath = monitoringDict[absPath]

    print("MONITORING", absPath)
    files = os.listdir(absPath)
    isGitRepo = ".git" in files
    if isGitRepo:
        print("GIT REPO FOUND.")
        # if init:
        #     os.system("rm -rf .git")
    if init == "":
        # pass# do work on initialized repo.
        fileNames, dirNames, symLinks = checkStatus()
        changeLog = "FILE:\n{}\n\nDIR:\n{}\n\nSYMLINK:{}\n\n".format(
            "\n".join(fileNames), "\n".join(dirNames), "\n".join(symLinks)
        )
        report = getStatusReport(fileNames, dirNames, symLinks)
        processReport(report, init=False, changeLog=changeLog)
        # then commit.
    else:
        # git@github.com:James4Ever0/pyjom.git
        assert init.startswith("git@")
        assert init.endswith(".git")
        # we use ssh key only now.
        # if not init.endswith(".git"):
        #     init += ".git"
        print("remote git url:", init)
        if isGitRepo:  # must remove that .git
            print("removing base git folder")
            gitBase = os.path.join(absPath, ".git")
            removePath(gitBase)

        report = scanPath(absPath)
        processReport(report, init=True, init_url=init)
