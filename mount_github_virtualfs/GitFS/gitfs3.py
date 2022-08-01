#!/usr/bin/env python
#
# Use Git as a Storage Filesystem
#
# Copyright (c) 2011 Sreejith K <sreejitemk@gmail.com>
# Licensed under FreeBSD License. Refer COPYING for more information
#
# http://foobarnbaz.com
# Created on 11th Jan 2011




from errno import EACCES
from sys import argv, exit
from time import time
from time import sleep
import logging
import datetime
import os
from threading import Lock, Condition, Thread, Event

from fuse3 import FUSE, FuseOSError, Operations, LoggingMixIn
import pygit2 # exceptions?

class GitStatus(object):

    def __init__(self, path):
        if not os.getcwd() == path:
            os.chdir(path)
        self.status = {}

    def update(self):
        self.clear()
        logging.debug('getting status')
        for line in os.popen('git status').readlines():
            line = line.strip()
            if line.startswith('#\t'):
                try:
                    status, file = [l.strip() for l in line[2:].split(':')]
                    if file in self.status:
                        self.status[status].append(file)
                    else:
                        self.status[status] = [file]
                except ValueError:
                    if 'untracked' in self.status:
                        self.status['untracked'].append( line[2:].strip() )
                    else:
                        self.status['untracked'] = [ line[2:].strip() ]
        logging.debug('current status: %r' %self.status)
        return self.status

    def stagedFiles(self):
        self.update()
        return self.status.get('renamed',  []) + \
               self.status.get('modified', []) + \
               self.status.get('new file', []) + \
               self.status.get('deleted',  [])

    def unstagedFiles(self):
        self.update()
        return self.status.get('untracked', [])

    def clear(self):
        self.status.clear()

class GitRepo(object):

    def __init__(self, path, origin, branch, sync=False):
        self.path = path
        self.origin = origin
        self.branch = branch
        self.status = GitStatus(path)
        # sync all the files with git
        if sync:
            self.synchronize()

    def synchronize(self):
        logging.debug('syncing')
        self.pull()
        # if self.syncNeeded():
            # unstaged = self.status.unstagedFiles()
        self.stage(".")
        # for file in unstaged:
        #     self.stage(file)
        self.commit('syncing files @ %s' %datetime.datetime.now())
        self.push()

    def syncNeeded(self):
        return True
        # return (self.status.stagedFiles() + self.status.unstagedFiles() and True or False)
    
    def pull(self):
        logging.debug('pulling files')
        os.system('git pull origin %s ' %self.branch)

    def stage(self, _file):
        _file="." # override.
        logging.debug('staging file %s' % _file)
        os.system('git add %s' % _file)

    def commit(self, msg):
        logging.debug('commiting file %s' % file)
        os.system('git commit -am \"%s\"' % msg)

    def push(self):
        logging.debug('pushing')
        os.system('git push origin %s' % self.branch)
        self.status.clear()

class GitFS(LoggingMixIn, Operations):
    """A simple filesystem using Git and FUSE.
    """
    def __init__(self, origin, branch='master', path='.'):
        self.origin = origin
        self.branch = branch
        self.root = os.path.realpath(path)
        self.repo = GitRepo(path, origin, branch, sync=True)
        self.halt = False
        self.rwlock = Lock()
        self.sync_c = Condition()
        self.sync_event = Event()
        self.sync_event.clear()
        self.file_updated = False
        self.sync_thread = Thread(target=self._sync, args=())
        self.sync_thread.start()

    def _sync(self):
        while True:
            # self.sync_c.acquire()
            if not self.halt:
                # # wait till a sync request comes
                # self.sync_c.wait()
                # if self.file_updated:
                self.sync_event.wait()
                self.sync_event.clear()
                self.repo.synchronize()
                print("SYNCING")
                # self.sync_c.release()
            else:
                # self.sync_c.release()
                break
    def notify(self):
        # self.file_updated=True
        self.sync_event.set()
        # self.sync_c.acquire()
        # self.sync_c.notifyAll()
        # self.sync_c.release()

    def destroy(self, path):
        # stop sync thread
        self.sync_c.acquire()
        self.halt = True
        self.sync_c.notifyAll()
        self.sync_c.release()
    
    def __call__(self, op, path, *args):
        return super(GitFS, self).__call__(op, self.root + path, *args)
    
    def access(self, path, mode):
        if not os.access(path, mode):
            raise FuseOSError(EACCES)
    
    chmod = os.chmod
    chown = os.chown
    
    def create(self, path, mode):
        value = os.open(path, os.O_WRONLY | os.O_CREAT, mode)
        self.notify()
        return value
    
    def flush(self, path, fh):
        return os.fsync(fh)

    def fsync(self, path, datasync, fh):
        return os.fsync(fh)
                
    def getattr(self, path, fh=None):
        st = os.lstat(path)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
            'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
    
    getxattr = None
    
    def link(self, target, source):
        return os.link(source, target)
    
    listxattr = None
    def mkdir(self, path, mode):
        value = os.mkdir(path, mode)
        self.notify()
        return value
    mknod = os.mknod
    open = os.open
        
    def read(self, path, size, offset, fh):
        with self.rwlock:
            os.lseek(fh, offset, 0)
            return os.read(fh, size)
    
    def readdir(self, path, fh):
        return ['.', '..'] + os.listdir(path)

    readlink = os.readlink
    
    def release(self, path, fh):
        return os.close(fh)
        
    def rename(self, old, new):
        value = os.rename(old, self.root + new)
        self.notify()
        return value
    
    def rmdir(self, path):
        value = os.rmdir(path)
        self.notify()
        return value
    
    def statfs(self, path):
        stv = os.statvfs(path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))
    
    def symlink(self, target, source):
        return os.symlink(source, target)
    
    def truncate(self, path, length, fh=None):
        with open(path, 'r+') as f:
            f.truncate(length)
        self.notify()

    
    def unlink(self,path):
        value = os.unlink(path)
        self.notify()
        return value
    utimens = os.utime
    
    def write(self, path, data, offset, fh):
        with self.rwlock:
            os.lseek(fh, offset, 0)
            value = os.write(fh, data)
            self.notify()
            return value

    

if __name__ == "__main__":
    if len(argv) != 5:
        print('usage: %s <origin> <branch> <local_repo> <mount_point>' % argv[0])
        exit(1)
    fuse = FUSE(GitFS(argv[1], argv[2], argv[3]), argv[4], foreground=True)
