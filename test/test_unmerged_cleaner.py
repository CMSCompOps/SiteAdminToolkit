#! /usr/bin/env python

"""
``test/test_unmerged_cleaner.py`` performs the unit tests for the :ref:`unmerged-ref`.
The script can take two optional arguments for testing for the file system at your site.

- The first argument is the location of the folder to be tested.
  This should be a location that does not exist, and it should be in a location managed
  by the filesystem to test.
- The second argument is the type of filesystem testing for.
  See :ref:`listdel-config-ref` for the currently supported file system types.

:author: Daniel Abercrombie <dabercro@mit.edu>
"""


import os
import sys
import unittest
import random
import uuid
import testfixtures
import time
import shutil

import CMSToolBox._loadtestpath
import ListDeletable


# Check if the place to do the test is already used or not
unmerged_location = ListDeletable.config.UNMERGED_DIR_LOCATION


if os.path.exists(unmerged_location):
    print ('Path %s already exists. Refusing to do unit tests.' % 
           unmerged_location)
    exit()
else:
    print 'Running test at %s' % unmerged_location


protected_list = ['protected1', 'dir/that/is/protected', 'delete/except/protected']
ListDeletable.PROTECTED_LIST = [os.path.join(ListDeletable.config.LFN_TO_CLEAN, protected) \
                                    for protected in protected_list]
ListDeletable.PROTECTED_LIST.sort()
ListDeletable.ALL_LENGTHS = list(set(
        len(protected) for protected in ListDeletable.PROTECTED_LIST))
ListDeletable.ALL_LENGTHS.sort()


class TestUnmergedFunctions(unittest.TestCase):

    def test_search_numbers(self):
        test_list = random.sample(xrange(1000000), 10000)
        test_list.sort()

        for i in range(100):
            element = test_list[int(random.random() * len(test_list))]
            self.assertEqual(ListDeletable.bi_search(test_list, element),
                             True, 'bi_search did not find number when it should.')

            popped = test_list.pop(int(random.random() * len(test_list)))
            self.assertEqual(ListDeletable.bi_search(test_list, popped),
                             False, 'bi_search found a number when it should not.')

    def test_search_strings(self):
        test_list = list(set(str(uuid.uuid4()) for i in range(1000)))
        test_list.sort()

        for i in range(100):
            element = test_list[int(random.random() * len(test_list))]
            self.assertEqual(ListDeletable.bi_search(test_list, element),
                             True, 'bi_search did not find string when it should.')

            popped = test_list.pop(int(random.random() * len(test_list)))
            self.assertEqual(ListDeletable.bi_search(test_list, popped),
                             False, 'bi_search found a string when it should not.')

    def test_get_protected(self):
        protected = ListDeletable.get_protected()
        self.assertTrue(isinstance(protected, list), 'Protected list is not a list.')
        self.assertNotEqual(len(protected), 0, 'Protected list is empty.')
        for one_dir in protected:
            self.assertTrue(one_dir.startswith('/store/'),
                            'Protected directory %s does not have expected LFN.' % one_dir)


class TestUnmergedFileChecks(unittest.TestCase):

    tmpdir = None

    def setUp(self):
        self.tmpdir = testfixtures.TempDirectory(path=unmerged_location)

    def tearDown(self):
        self.tmpdir.cleanup()
        if os.path.exists(unmerged_location):
            shutil.rmtree(unmerged_location)

    def test_size(self):
        for log_size in range(1, 7):
            size = 10 ** log_size
            tmp_file = self.tmpdir.write('size/file_{0}'.format(size),
                                         bytearray(os.urandom(size)))

            self.assertEqual(ListDeletable.get_file_size(tmp_file), size,
                             'get_file_size is returning wrong value -- %s for %s.' %
                             (ListDeletable.get_file_size(tmp_file), size))

    def test_time(self):
        print 'Testing timing. Will take a few seconds.'
        start_time = time.time()
        time.sleep(2)
        tmp_file = self.tmpdir.write('time/file.txt', 'Testing time since created.')
        time.sleep(2)
        after_create = time.time()

        self.assertTrue(ListDeletable.get_mtime(tmp_file) >= int(start_time),
                        'File appears older than it actually is.')

        self.assertTrue(ListDeletable.get_mtime(tmp_file) <= int(after_create),
                        'File appears newer than it actually is.')

    def do_deletion(self, delete_function):
        # Pass a function that does the deletion

        to_delete = ['delete/not/protected', 'dir/to/delete', 'make/a/dir/to/delete', 'hello/delete']
        touched_new = ['touch/this']
        too_new = ['hello/new', 'new']
        all_dirs = to_delete + too_new + touched_new + \
            ListDeletable.config.DIRS_TO_AVOID + protected_list

        start_time = time.time()
        for next_dir in all_dirs:
            if next_dir not in too_new:
                self.tmpdir.write(os.path.join(next_dir, 'test_file.root'),
                                  bytearray(os.urandom(1024)))

        print 'Waiting for some time.'

        time.sleep(5)
        cutoff_time = int(time.time())
        time.sleep(5)

        for next_dir in too_new:
            self.tmpdir.write(os.path.join(next_dir, 'test_file.root'),
                              bytearray(os.urandom(1024)))
        for next_dir in touched_new:
            os.utime(self.tmpdir.getpath(os.path.join(next_dir, 'test_file.root')),
                     None)

        ListDeletable.config.MIN_AGE = int(time.time() - cutoff_time)
        ListDeletable.NOW = int(time.time())
        ListDeletable.main()

        delete_function() # Function that does deletion is done here

        for dir in all_dirs:
            check_file = self.tmpdir.getpath(os.path.join(dir, 'test_file.root'))
            self.assertEqual(os.path.exists(check_file), dir not in to_delete,
                             'File status is unexpected: %s' % check_file)

    def test_deletions(self):
        methods = {
            'posix': [
                ListDeletable.do_delete
                ],         # Test the do_delete function
            'Hadoop': [
                ListDeletable.do_delete,               # Test the do_delete function
# The Perl script is not configurable enough for unit tests at the moment
#                lambda: os.system(                     # Test the Perl script
#                    '%s %s' % (
#                        os.path.join(os.path.dirname(__file__), '../unmerged-cleaner/HadoopDelete.pl'),
#                        ListDeletable.config.DELETION_FILE
#                        )
#                    )
                ],
            'dCache': []
            }

        for i, method in enumerate(methods[ListDeletable.config.STORAGE_TYPE]):
            for which in ['directories', 'files']:

                print '%s using %s' % (ListDeletable.config.STORAGE_TYPE, which)

                ListDeletable.config.WHICH_LIST = which

                self.tearDown()
                self.setUp()

                self.do_deletion(method)

if __name__ == '__main__':
    unittest.main()
