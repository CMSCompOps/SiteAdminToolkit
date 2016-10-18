#! /usr/bin/env python

"""
This script is located as ``SiteAdminToolkit/unmerged-cleaner/UnmergedCleaner.py``.
It is used to clean up unmerged files, leaving protected directories alone.
In order to use the script at your site, make sure you specify your storage
system. The only command that depends on you FS is a command that lists directories.
The script will write a list of directories that can be removed. For now we
leave to site admins to correctly remove those directories. For Hadoop users
we provide a script that will do such removal as I(Max) do it on MIT cluster.
:author: Chistoph Wissing + Dan Abercrombi + Max Goncharov
"""
import os, sys, re, glob, time
import httplib
import simplejson as json

#define your storage, configurable
myStorage = 'Hadoop'
#define the full pathename for your system, configurable
fullStub = '/mnt/hadoop/cms'
#where you want directories that can be deleted written, configurable
fileName = '/root/files2delete.txt'
#directories to exclude from consideration, configurable
dirsToAvoid = ['SAM','log']
#minimum time interval when we can start deleting(one week now)
minTimeWindow = 60*60*24*7

moreStub = '/store/unmerged'
protectedList = []
nameLength = []

nowTime = int(time.time())

class DataNode:
    def __init__(self,pathName):
	self.pathName = pathName
	self.subNodes = []
	self.canVanish = None
	self.latest = 0
	self.nsubnodes = 0
	self.nsubfiles = 0
	self.size = 0

    def Fill(self):
	if bi_search(nameLength,len(self.pathName)):
	    if bi_search(protectedList, self.pathName):
	        self.canVanish = False
	        return

	#here we invoke method that might not work on all 
	#storage systems
	fullPathName = fullStub + self.pathName
	dirs = listFolder(fullPathName,'subdirs')
	allFiles = listFolder(fullPathName,'files')
	for subdir in dirs:
	    sub_node = DataNode(self.pathName + '/' + subdir)
	    sub_node.Fill()
	    self.subNodes.append(sub_node)
	#get the latest modification start for all files
	for file in allFiles:
	    modtime = getMtime(fullPathName + '/' + file)
            self.size = self.size + getFileSize(fullPathName + '/' + file)
            if modtime > self.latest:
                self.latest = modtime
	
	self.canVanish = True
	for sub_node in self.subNodes:
	    self.nsubnodes = self.nsubnodes + sub_node.nsubnodes + 1
	    self.nsubfiles = self.nsubfiles + sub_node.nsubfiles 
	    self.size = self.size + sub_node.size
	    if sub_node.canVanish == False:
		self.canVanish = False
	    if sub_node.latest > self.latest:
                self.lastest = sub_node.latest
	self.nsubfiles = self.nsubfiles + len(allFiles)
	if self.nsubnodes == 0 and self.nsubfiles == 0:
	    self.latest = getMtime(fullPathName)
	
	if (nowTime - self.latest) < minTimeWindow:
	    self.canVanish = False

def traverseTree(node,list2del):
    if node.canVanish:
        list2del.append(node)
        return
    for sub_node in node.subNodes:
        traverseTree(sub_node,list2del)

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

def bi_search(thelist, item):
    if len(thelist) == 0:
        return False
    else:
        mid = len(thelist)//2
        if thelist[mid]==item:
          return True
        else:
          if item<thelist[mid]:
            return bi_search(thelist[:mid],item)
          else:
            return bi_search(thelist[mid+1:],item)

def listFolder(name,opt):
    #this is where the call is made depending on what
    #sile system the site is running, should add more as we go on
    if myStorage == 'Hadoop':
	return lsHadoop(name,opt)
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

def lsHadoop(name,opt):
    path, dirs, files = os.walk(name).next()
    if opt == 'subdirs':
	return dirs
    else:
	return files

def getMtimeHadoop(name):
    return int(os.stat(name).st_mtime)

def getFileSizeHadoop(name):
   #convert to MBs
   return int(os.stat(name).st_size)

#get a list of protected directories
#that can't be deleted
protectedList = get_protected()
protectedList.sort()

allLength = []
for item in protectedList:
    allLength.append(len(item))
nameLength = list(set(allLength))    

#list all subdirs in the top directory
#then build a tree for each subnode, avoid logs
#now build a directory tree of directories to delete
print "Some statistics about what is going to be deleted"
print "# Folders  Total    Total  DiskSize  FolderName"
print "#          Folders  Files  [GB]                "

dirs = listFolder(fullStub + moreStub,'subdirs')
dirsToDelete = []
for subdir in dirs:
    skip = False
    for item in dirsToAvoid:
        if item in subdir:
	    skip = True
	    break
    if skip:
	continue
    topNode = DataNode(moreStub + '/' + subdir)
    topNode.Fill()

    list2del = []
    traverseTree(topNode,list2del)
    if len(list2del) < 1 :
	continue
    totDirs2Del = 0
    totFiles2Del = 0
    totSize2Del = 0
    for item in list2del:
	totDirs2Del = totDirs2Del + item.nsubnodes
	totFiles2Del = totFiles2Del + item.nsubfiles
	totSize2Del = totSize2Del + item.size
    totSize2Del = totSize2Del/(1024*1024*1024)
    print "  %-8d %-8d %-6d %-9d %-s"\
	%(len(list2del),totDirs2Del,totFiles2Del,totSize2Del,subdir)
    dirsToDelete.extend(list2del)

del_file = open(fileName, 'w')
for item in dirsToDelete:
	del_file.write(item.pathName+'\n')
del_file.close()
