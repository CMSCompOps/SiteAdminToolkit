#! /usr/bin/env python

"""
This script is located as ``SiteAdminToolkit/unmerged-cleaner/CleanUnmerged.py``.
It is used to clean up unmerged files, leaving protected directories alone.

In order to use the script at your site, make sure you specify your storage
system. The only command that depends on you FS is a command that lists directories.
The script will write a list of directories that can be removed. For now we
leave to site admins to correctly remove those directories. For Hadoop users
we provide a script that will do such removal as I(Max) do it on MIT cluster.

:authors: Chistoph Wissing <christoph.wissing@desy.de> and
          Max Goncharov <maxi@mit.edu>
"""

import os
import time
import subprocess
import signal
import httplib

try:
    import simplejson as json
except ImportError:
    import json

# define your storage, configurable
myStorage = 'Hadoop'
# define the name of your site, configurable
mySite = 'T2_US_MIT'
# where you want directories that can be deleted written, configurable
fileName = '/root/files2delete.txt'
# directories to exclude from consideration, configurable
dirsToAvoid = ['SAM', 'logs']
# minimum time interval when we can start deleting(one week now)
minTimeWindow = 60 * 60 * 24 * 7

pfnPath = None
lfnPath = None
protectedList = []
nameLength = []
nowTime = int(time.time())


class Alarm(Exception):
    pass


def alarm_handler(signum, frame):
    raise Alarm


class DataNode(object):
    def __init__(self, pathName):
        self.pathName = pathName
        self.subNodes = []
        self.canVanish = None
        self.latest = 0
        self.nsubnodes = 0
        self.nsubfiles = 0
        self.size = 0

    def Fill(self):
        lfnPathName = lfnPath + self.pathName
        if bi_search(nameLength, len(lfnPathName)) and \
                bi_search(protectedList, lfnPathName):
            self.canVanish = False
            return

        # here we invoke method that might not work on all
        # storage systems
        fullPathName = pfnPath + self.pathName
        dirs = listFolder(fullPathName, 'subdirs')
        allFiles = listFolder(fullPathName, 'files')
        for subdir in dirs:
            sub_node = DataNode(self.pathName + '/' + subdir)
            sub_node.Fill()
            self.subNodes.append(sub_node)
            # get the latest modification start for all files
        for file_name in allFiles:
            modtime = getMtime(fullPathName + '/' + file_name)
            self.size = self.size + getFileSize(fullPathName + '/' + file_name)
            if modtime > self.latest:
                self.latest = modtime

        self.canVanish = True
        for sub_node in self.subNodes:
            self.nsubnodes = self.nsubnodes + sub_node.nsubnodes + 1
            self.nsubfiles = self.nsubfiles + sub_node.nsubfiles
            self.size = self.size + sub_node.size
            if not sub_node.canVanish:
                self.canVanish = False
            if sub_node.latest > self.latest:
                self.lastest = sub_node.latest
        self.nsubfiles = self.nsubfiles + len(allFiles)
        if self.nsubnodes == 0 and self.nsubfiles == 0:
            self.latest = getMtime(fullPathName)

        if (nowTime - self.latest) < minTimeWindow:
            self.canVanish = False


def traverseTree(node, list2del):
    if node.canVanish:
        list2del.append(node)
        return
    for sub_node in node.subNodes:
        traverseTree(sub_node, list2del)


def get_protected():
    """
    :returns: the protected directory LFNs.
    :rtype: list
    """

    url = 'cmst2.web.cern.ch'
    conn = httplib.HTTPSConnection(url)

    try:
        conn.request('GET', '/cmst2/unified/listProtectedLFN.txt')
        res = conn.getresponse()
        result = json.loads(res.read())
    except TypeError:
        print 'Cannot read Protected LFNs. Have to stop...'
        exit(1)

    protected = result['protected']
    conn.close()

    uniqList = list(set(protected))
    return uniqList


def get_lfn(siteName):
    webServer = 'https://cmsweb.cern.ch/phedex/datasvc/json/prod/'
    args = 'lfn2pfn?node=' + siteName + '&protocol=direct&lfn=/store/unmerged/'

    url = '"' + webServer + args + '"'
    cmd = 'curl -k -H "Accept: text/xml" ' + url

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               bufsize=4096, shell=True)

    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(5 * 60)  # 5 minutes

    try:
        strout, _ = process.communicate()
        signal.alarm(0)
    except Alarm:
        print " Oops, taking too long!"
        raise Exception(" FATAL -- Call to PhEDEx timed out, stopping")

    if process.returncode != 0:
        print " Received non-zero exit status: " + str(process.returncode)
        raise Exception(" FATAL -- Call to PhEDEx failed, stopping")

    dataJson = json.loads(strout)
    pfn = dataJson["phedex"]["mapping"][0]["pfn"]
    lfn = dataJson["phedex"]["mapping"][0]["lfn"]
    del dataJson
    return (pfn, lfn)


def bi_search(thelist, item):
    if len(thelist) == 0:
        return False
    else:
        mid = len(thelist) // 2
        if thelist[mid] == item:
            return True
        else:
            if item < thelist[mid]:
                return bi_search(thelist[:mid], item)
            else:
                return bi_search(thelist[mid + 1:], item)


def listFolder(name, opt):
    # this is where the call is made depending on what
    # sile system the site is running, should add more as we go on
    if myStorage == 'Hadoop':
        return lsHadoop(name, opt)
    else:
        return None


def getMtime(name):
    if myStorage == 'Hadoop':
        return getMtimeHadoop(name)
    else:
        return None


def getFileSize(name):
    if myStorage == 'Hadoop':
        return getFileSizeHadoop(name)
    else:
        return None


def lsHadoop(name, opt):
    _, dirs, files = os.walk(name).next()
    if opt == 'subdirs':
        return dirs
    else:
        return files


def getMtimeHadoop(name):
    return int(os.stat(name).st_mtime)


def getFileSizeHadoop(name):
    return int(os.stat(name).st_size)


if __name__ == "__main__":

    # get a list of protected directories
    # that can't be deleted
    protectedList = get_protected()
    protectedList.sort()

    allLength = []
    for item in protectedList:
        allLength.append(len(item))
    nameLength = list(set(allLength))

    pfnPath, lfnPath = get_lfn(mySite)

    # list all subdirs in the top directory
    # then build a tree for each subnode, avoid logs
    # now build a directory tree of directories to delete
    print "Some statistics about what is going to be deleted"
    print "# Folders  Total    Total  DiskSize  FolderName"
    print "#          Folders  Files  [GB]                "

    dirs = listFolder(pfnPath, 'subdirs')
    dirsToDelete = []
    for subdir in dirs:
        if subdir in dirsToAvoid:
            continue

        topNode = DataNode(subdir)
        topNode.Fill()

        list2del = []
        traverseTree(topNode, list2del)
        if len(list2del) < 1:
            continue
        totDirs2Del = 0
        totFiles2Del = 0
        totSize2Del = 0
        for item in list2del:
            totDirs2Del = totDirs2Del + item.nsubnodes
            totFiles2Del = totFiles2Del + item.nsubfiles
            totSize2Del = totSize2Del + item.size
        totSize2Del = totSize2Del / (1024 * 1024 * 1024)
        print "  %-8d %-8d %-6d %-9d %-s" \
              % (len(list2del), totDirs2Del, totFiles2Del, totSize2Del, subdir)
        dirsToDelete.extend(list2del)

    del_file = open(fileName, 'w')
    for item in dirsToDelete:
        del_file.write(lfnPath + item.pathName + '\n')
    del_file.close()
