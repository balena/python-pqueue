"""A single process, persistent multi-producer, multi-consumer queue."""

import pickle
import os
import struct
import tempfile
import fcntl
from contextlib import closing

import sys
if sys.version_info < (3, 0):
    from Queue import Queue as SyncQ
else:
    from queue import Queue as SyncQ

class WriteBatch(object):
    def __init__(self, qfile, info):
        self.qfile = qfile
        self.info = info
        self.fd = open(qfile, 'ab')

    def write(self, string):
        self.fd.write(string)

    def item_done(self):
        hnum, hpos, _ = self.info['head']
        hpos += 1
        if hpos == self.info['chunksize']:
            hpos = 0
            hnum += 1
        self.info['size'] += 1
        hoffset = self.fd.tell()
        self.info['head'] = [hnum, hpos, hoffset]

    def close(self):
        self.fd.close()

class Lock(object):
    def __init__(self, lockfile):
        self.lockfile = lockfile
        self.fd = open(lockfile, 'w')
        fcntl.lockf(self.fd.fileno(), fcntl.LOCK_EX)

    def close(self):
        fcntl.lockf(self.fd.fileno(), fcntl.LOCK_UN)
        self.fd.close()

class Queue(SyncQ):

    """Create a persistent queue object on a given path.

    The argument path indicates a directory where enqueued data should be
    persisted. If the directory doesn't exist, one will be created. If maxsize
    is <= 0, the queue size is infinite. The optional argument chunksize
    indicates how many entries should exist in each chunk file on disk.
    """
    def __init__(self, path, maxsize=0, chunksize=100):
        self.path = path
        self.chunksize = chunksize
        SyncQ.__init__(self, maxsize)

    def _init(self, maxsize):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
            open(self._lockfile(), 'w').close()
        # trucate head case it contains garbage
        info = self._loadinfo()
        hnum, hcnt, hoffset = info['head']
        head = self._qfile(hnum)
        if os.path.exists(head):
            if hoffset < os.path.getsize(head):
                os.truncate(head, hoffset)

    def _qsize(self, len=len):
        with closing(Lock(self._lockfile())):
            return self._loadinfo()['size']

    def _put(self, item):
        with closing(Lock(self._lockfile())):
            info = self._loadinfo()
            hnum, hpos, _ = info['head']
            with closing(WriteBatch(self._qfile(hnum), info)) as headf:
                pickle.dump(item, headf)
                headf.item_done()
                self._saveinfo(headf.info)

    def _get(self):
        with closing(Lock(self._lockfile())):
            info = self._loadinfo()
            tnum, tcnt, toffset = info['tail']
            hnum, hcnt, _ = info['head']
            if [tnum, tcnt] >= [hnum, hcnt]:
                return None
            with self._opentail(info) as tailf:
                data = pickle.load(tailf)
                toffset = tailf.tell()
            tcnt += 1
            if tcnt == info['chunksize'] and tnum <= hnum:
                tcnt = toffset = 0
                tnum += 1
                os.remove(tailf.name)
            info['size'] -= 1
            info['tail'] = [tnum, tcnt, toffset]
            self._saveinfo(info)
        return data

    def _openchunk(self, number):
        return open(self._qfile(number), 'rb')

    def _opentail(self, info):
        tailf = self._openchunk(info['tail'][0])
        tailf.seek(info['tail'][2])
        return tailf

    def _loadinfo(self):
        infopath = self._infopath()
        if os.path.exists(infopath):
            with open(infopath) as f:
                info = pickle.load(f)
        else:
            info = {
                'chunksize': self.chunksize,
                'size': 0,
                'tail': [0, 0, 0],
                'head': [0, 0, 0],
            }
        return info

    def _saveinfo(self, info):
        tmpfd, tmpfn = tempfile.mkstemp()
        os.write(tmpfd, pickle.dumps(info))
        os.close(tmpfd)
        # POSIX requires that 'rename' is an atomic operation
        os.rename(tmpfn, self._infopath())

    def _qfile(self, number):
        return os.path.join(self.path, 'q%05d' % number)

    def _lockfile(self):
        return os.path.join(self.path, '.lock')

    def _infopath(self):
        return os.path.join(self.path, 'info')

