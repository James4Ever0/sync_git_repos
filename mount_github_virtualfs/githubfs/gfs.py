#!/usr/bin/env python3

# GITHUB HAS RATE LIMIT ON THOSE APIS. THUS NO AUTOSAVE?
# github rate limits will be reset every per 10 minutes?

# actually, per hour. really? for github apps.
import traceback

import os
import sys
import errno

# import getpass
import pwd

os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""

from stat import S_IFDIR, S_IFLNK, S_IFREG, S_ISREG
from github import Github
import github
from fuse import FUSE, FuseOSError, Operations
from time import time, mktime, sleep

credentials = {
    "username": "James4Ever0",
    "pass": "k2dpxihmm563b9n",
    "token": "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",
}
targetRepo = "toyProject"  # not my dearly repo!
repoBranch = "master"
# repoBranch = "main"
# need to change repo.get_contents. lazy loading the content inside each file/dir.

# need we create a shadow copy of existing contents?
def todict(obj, classkey=None):
    return obj.raw_data

class gfs(Operations):
    def __init__(self, shadowCopyPath):
        assert os.path.isabs(shadowCopyPath)
        shadowCopyRepo = os.path.join(shadowCopyPath, targetRepo)
        print("[init]: github fs on repo: %s" % targetRepo)
        print("[init]: github fs shadowCopy abspath: %s" % shadowCopyRepo)
        self.user = Github(credentials["token"])
        # self.user = Github(credentials["username"],credentials["pass"])
        self.branch = repoBranch

        print("[init]: Establishing connection....")
        self.objectProperties = {}
        self.fileSizes = {}
        self.pathDict = {}  # already fetched directories.
        self.pathSet = set("/")  # root path of a given repo.
        print("[init]: Fetching repositories...")
        self.file_content_bytes = dict()
        # self.file_content_bytes = dict()
        self.user = self.user.get_user(credentials["username"])
        print("GET USER", self.user)
        self.repo = self.user.get_repo(targetRepo)
        # only select the dedicated repo
        print("REPOSITORY NAME", self.repo.name)
        # self.repo_list.append(self.repo.name)
        print("Done")

    def open(self, path, flags):
        print("[open]", path)
        # self.repo.create_file
        if path == "/" or path in self.pathSet:
            pass
        else:
            dirpath, name = self.getPathComponents(path)
            if dirpath in self.file_content_bytes.keys():  # is it even updated?
                if name in self.file_content_bytes[dirpath].keys():
                    data = self.file_content_bytes[dirpath][name]
                    return len(data)
                else:
                    self.create(path, None)
                    return 0
            fileContent = self.repo.get_contents(path)
            len_content, content = self.updateScannedFile(fileContent, dirpath, name)
            return len(content)


    def updateScannedFile(self, fileContent, dirpath, name):
        content = fileContent.decoded_content
        if dirpath not in self.file_content_bytes.keys():
            self.file_content_bytes[dirpath] = {}
        self.file_content_bytes[dirpath].update({name: content})
        return len(content), content

    def getattr(self, path, fh=None):
        print("[getattr]: ", path)
        properties = dict(
            st_mode=S_IFDIR | 755,
            st_nlink=2,
            st_ctime=0,
            st_mtime=0,
            st_atime=0,
            st_uid=pwd.getpwuid(os.getuid()).pw_uid,
            st_gid=pwd.getpwuid(os.getuid()).pw_gid,
        )
        if path == "/" or path in self.pathSet:
            pass
        else:
            file_size = 4096
            # isfile=False
            if path not in self.fileSizes.keys():
                return dict(
                    st_mode=S_IFREG | 644,
                    st_size=0,
                    st_nlink=1,
                )  # to create new file, one must change this.
            # unknown file. at least not registered.
            # if isfile:
            file_size = self.fileSizes[path]
            properties = dict(
                st_mode=S_IFREG | 644,
                st_size=file_size,
                st_nlink=1,
            )
        return properties

    def create(self, path, mode):
        # must be file?
        print("[create] path: %s" % path)
        if path in self.fileSizes.keys() or path in self.pathSet: return 0
        if path.startswith("/"):path = path[1:]
        baseName = os.path.basename(path)
        if baseName == ".git": return
        response = self.repo.create_file(
            path, "create file {}".format(path), "", branch=self.branch
        )
        dirpath, name = self.getPathComponents(path)
        # print(response["content"])
        # breakpoint()

        self.pathDict[dirpath].update({name: todict(response["content"])})
        self.fileSizes.update({path: 0})
        self.file_content_bytes[dirpath][name] = bytes()
        return 0

    def getPathComponents(self, path):
        return os.path.dirname(path), os.path.basename(path)

    def read(self, path, size, offset, fh=None):
        print("[read]: ", path)
        # file_content = ""
        if path == "/" or path in self.pathSet:
            pass
        else:
            dirpath, name = self.getPathComponents(path)
            if dirpath not in self.file_content_bytes.keys():
                fileContent = self.repo.get_contents(path)
                self.updateScannedFile(fileContent, dirpath, name)
            return self.file_content_bytes[dirpath][name][offset : offset + size]

    def write(self, path, data, offset, fh):
        print("[write] %s" % path)
        dirpath, name = self.getPathComponents(path)
        if dirpath in self.file_content_bytes.keys():
            if name not in self.file_content_bytes[dirpath].keys():
                self.create(path, None)
            self.file_content_bytes[dirpath][name] = (
                # make sure the data gets inserted at the right offset
                self.file_content_bytes[dirpath][name][:offset].ljust(
                    offset, "\x00".encode("ascii")
                )
                + data
                # and only overwrites the bytes that data is replacing
                + self.file_content_bytes[dirpath][name][offset + len(data) :]
            )
            sha = self.pathDict[dirpath][name]["sha"]
            self.fileSizes[path] = len(self.file_content_bytes[dirpath][name])
            result = self.repo.update_file(
                path,
                "Update file {}".format(path),
                self.file_content_bytes[dirpath][name],
                sha,
                branch=self.branch,
            )
            self.pathDict[dirpath][name] = todict(result["content"])
            return len(data)

    def mkdir(self, path, mode):
        print("[mkdir] {}".format(path))
        if path not in self.pathSet:  # not gonna upload to github.
            self.pathSet.add(path)
            self.pathDict.update({path: []})

    def rmdir(self, path):
        print("[rmdir] {}".format(path))
        if path == "/":
            pass  # we do not have sha for root directory
        if path in self.pathSet:
            self.pathSet.discard(path)
            del self.pathDict[path]  # do we need recursive operation?
            if path in self.file_content_bytes[path]:
                del self.file_content_bytes[path]
            # also sync with the cloud!
            dirpath, name = self.getPathComponents(path)
            sha = self.pathDict[dirpath][name]["sha"]
            del self.pathDict[dirpath][name]
            # is that going to work?
            self.repo.delete_file(
                path, "remove directory {}".format(path), sha, branch=self.branch
            )  # what is this sha?
        elif path in self.fileSizes.keys():
            dirpath, name = self.getPathComponents(path)
            del self.fileSizes[path]
            del self.file_content_bytes[dirpath][name]
            del self.pathDict[dirpath][name]
            self.repo.delete_file(
                path, "remove file {}".format(path), sha, branch=self.branch
            )

    def readdir(self, path, fh):
        print("[readdir]: ", path)
        repo_list = [".", ".."]
        if path.startswith("."):
            pass
        else:
            if path in self.pathSet:
                if path in self.pathDict.keys():
                    repo_list += list(self.pathDict[path].keys())
                else:

                    # sample item dict:
                    # {'name': '.gitignore', 'path': '.gitignore', 'sha': '0b231a1debec0cc6a90638376da5d9ddba32deb4', 'size': 1857, 'url': 'https://api.github.com/repos/James4Ever0/pyjom/contents/.gitignore?ref=main', 'html_url': 'https://github.com/James4Ever0/pyjom/blob/main/.gitignore', 'git_url': 'https://api.github.com/repos/James4Ever0/pyjom/git/blobs/0b231a1debec0cc6a90638376da5d9ddba32deb4', 'download_url': 'https://raw.githubusercontent.com/James4Ever0/pyjom/main/.gitignore?token=AYZN5DE3OD2QBYKHOCQTXKTC3PGUO', 'type': 'file', '_links': {'self': 'https://api.github.com/repos/James4Ever0/pyjom/contents/.gitignore?ref=main', 'git': 'https://api.github.com/repos/James4Ever0/pyjom/git/blobs/0b231a1debec0cc6a90638376da5d9ddba32deb4', 'html': 'https://github.com/James4Ever0/pyjom/blob/main/.gitignore'}}
                    files = self.repo.get_contents(path)
                    self.updateScannedDir(files, path)

        return repo_list

    def updateScannedDir(self, files, path):
        repo_list = []
        self.pathDict.update({path: {x["name"]: x for x in files}})
        for item in files:
            repo_list.append(item["name"])
            itemPath = os.path.join(path, item["name"])
            self.objectProperties.update(
                {itemPath: {"type": item["type"], "parent": path}}
            )

            if item["type"] == "dir":
                self.pathSet.add(itemPath)
            elif item["type"] == "file":
                updateDict = {itemPath: item["size"]}
                self.fileSizes.update(updateDict)
                print("UPDATE FILESIZE:", updateDict)
        return repo_list


def main(mountpoint, shadowCopyPath):
    FUSE(gfs(shadowCopyPath), mountpoint, nothreads=True, foreground=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
