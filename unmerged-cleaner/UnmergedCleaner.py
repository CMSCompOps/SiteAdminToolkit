#! /usr/bin/env python

"""
This script is located as ``SiteAdminToolkit/unmerged-cleaner/UnmergedCleaner.py``.
It is used to clean up unmerged files, leaving protected directories alone.

.. todo::

   Don't forget to write up full instructions and link to twiki after getting this to work.

In order to use the script at your site, make sure you specify your storage system.
The only command that depends on you FS is a command that lists directories.
The script will write a list of directories that can be removed.
For now we leave to site admins to correctly remove those directories.
For Hadoop users we provide a script that will do such removal as used on the MIT cluster.

%s

:authors: Chistoph Wissing <christoph.wissing@desy.de> \n
          Max Goncharov <maxi@mit.edu> \n
          Daniel Abercrombie <dabercro@mit.edu>
"""

import httplib
import json
import os
import time
from bisect import bisect_left

import ConfigTools

try:
    import config

except ImportError:
    print 'Generating default configuration...'
    ConfigTools.generate_default_config()
    print '\nConfiguration created at config.py.'
    print 'Please correct the default values to match your site'
    print 'and run this script again.'
    exit()


class DataNode(object):
    def __init__(self, path_name):
        self.path_name = path_name
        self.sub_nodes = []
        self.can_vanish = None
        self.latest = 0
        self.nsubnodes = 0
        self.nsubfiles = 0
        self.size = 0

    def fill(self):
        lfn_path_name = os.path.join(ConfigTools.LFN, self.path_name)

        if bi_search(ALL_LENGTHS, len(lfn_path_name)) and \
                bi_search(PROTECTED_LIST, lfn_path_name):
            self.can_vanish = False

        else:
            # here we invoke method that might not work on all
            # storage systems
            full_path_name = os.path.join(config.UNMERGED_DIR_LOCATION, self.path_name)
            dirs = list_folder(full_path_name, 'subdirs')
            all_files = list_folder(full_path_name, 'files')

            for subdir in dirs:
                sub_node = DataNode(self.path_name + '/' + subdir)
                sub_node.fill()
                self.sub_nodes.append(sub_node)
                # get the latest modification start for all files

            for file_name in all_files:
                modtime = get_mtime(full_path_name + '/' + file_name)
                self.size = self.size + get_file_size(full_path_name + '/' + file_name)
                if modtime > self.latest:
                    self.latest = modtime

            self.can_vanish = True

            for sub_node in self.sub_nodes:
                self.nsubnodes += sub_node.nsubnodes + 1
                self.nsubfiles += sub_node.nsubfiles
                self.size = self.size + sub_node.size
                if not sub_node.can_vanish:
                    self.can_vanish = False
                if sub_node.latest > self.latest:
                    self.lastest = sub_node.latest

            self.nsubfiles = self.nsubfiles + len(all_files)

            if self.nsubnodes == 0 and self.nsubfiles == 0:
                self.latest = get_mtime(full_path_name)

            if (NOW - self.latest) < config.MIN_AGE:
                self.can_vanish = False


    def traverse_tree(self, list_to_del):
        if self.can_vanish:
            list_to_del.append(self)
            return
        for sub_node in self.sub_nodes:
            sub_node.traverse_tree(list_to_del)


def bi_search(thelist, item):
    """Performs a binary search

    :param list thelist: is the list to search
    :param item: is the item to determine if it's in *thelist* or not
    :type item: int or str
    :returns: whether or not *item* is in *thelist*
    :rtype: bool
    """

    # Check that the list has non-zero length and
    # if the bisected result is equal to the search term
    if thelist and thelist[bisect_left(thelist, item)] == item:
        return True

    # If not returned True, then the item is not in the list
    return False


def list_folder(name, opt):
    """
    Lists the directories or files in a parent directory.

    :param str name: is the name of the directory to list.
    :param str opt: determines what to list inside the directory.
                    If 'subdirs', then only directories are listed.
                    If any other value, only files inside directory
                    *name* are listed.
    :returns: a list of directories or files in a directory.
    :rtype: list
    """

    # This is where the call is made depending on what
    # file system the site is running, should add more as we go on
    inside = os.listdir(name)
    if opt == 'subdirs':
        # Return list of directories
        return filter(os.path.isdir, inside)
    else:
        # Return list of files
        return filter(os.path.isfile, inside)


def get_mtime(name):
    return int(os.stat(name).st_mtime)


def get_file_size(name):
    return int(os.stat(name).st_size)


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
    except Exception:
        print 'Cannot read Protected LFNs. Have to stop...'
        exit(1)

    protected = result['protected']
    conn.close()

    return protected


def main():
    """
    Does the full listing for the site given in the :file:`config.py` file.
    """

    print "Some statistics about what is going to be deleted"
    print "# Folders  Total    Total  DiskSize  FolderName"
    print "#          Folders  Files  [GB]                "

    # Get the location of the PFN and the subdirectories there

    dirs = list_folder(config.UNMERGED_DIR_LOCATION, 'subdirs')

    dirs_to_delete = []

    for subdir in dirs:
        if subdir in config.DIRS_TO_AVOID:
            continue

        top_node = DataNode(subdir)
        top_node.fill()

        list_to_del = []
        top_node.traverse_tree(list_to_del)

        if len(list_to_del) < 1:
            continue

        num_todelete_dirs = 0   # Number of directories to be deleted
        num_todelete_files = 0  # Number of files to be deleted
        todelete_size = 0       # Amount of space to be deleted (in GB, eventually)

        for item in list_to_del:
            num_todelete_dirs += item.nsubnodes
            num_todelete_files += item.nsubfiles
            todelete_size += item.size

        todelete_size /= (1024 * 1024 * 1024)
        print "  %-8d %-8d %-6d %-9d %-s" \
              % (len(list_to_del), num_todelete_dirs, num_todelete_files,
                 todelete_size, subdir)

        dirs_to_delete.extend(list_to_del)

    del_file = open(config.DELETION_FILE, 'w')
    for item in dirs_to_delete:
        del_file.write(os.path.join(ConfigTools.LFN, item.path_name) + '\n')
    del_file.close()


# Generate documentation for the options in the configuration file.
__doc__ %= '\n'.join(['- **%s** - %s' % (var, ConfigTools.DOCS[var].replace('\n', ' ')) \
                          for var in ConfigTools.VAR_ORDER])

NOW = int(time.time())

if __name__ == '__main__':

    # The list of protected directories to not delete
    PROTECTED_LIST = get_protected()
    PROTECTED_LIST.sort()

    # The lengths of these protected directories for optimization
    ALL_LENGTHS = list(set(
        len(protected) for protected in PROTECTED_LIST))

    ALL_LENGTHS.sort()

    main()

else:

    PROTECTED_LIST = []
    ALL_LENGTHS = []
