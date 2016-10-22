#! /usr/bin/env python

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


# Set up some configuration for the test
if not os.path.exists('unmerged_results'):
    os.mkdir('unmerged_results')

unmerged_location = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'unmerged')
ListDeletable.config.UNMERGED_DIR_LOCATION = unmerged_location
ListDeletable.config.DELETION_FILE = 'unmerged_results/to_delete.txt'
ListDeletable.config.DIRS_TO_AVOID = ['avoid']

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

        element = test_list[int(random.random() * len(test_list))]
        self.assertEqual(ListDeletable.bi_search(test_list, element),
                         True, 'bi_search did not find number when it should.')

        popped = test_list.pop(int(random.random() * len(test_list)))
        self.assertEqual(ListDeletable.bi_search(test_list, popped),
                         False, 'bi_search found a number when it should not.')

    def test_search_strings(self):
        test_list = list(set(uuid.uuid4 for i in range(1000)))
        test_list.sort()

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
        shutil.rmtree(unmerged_location)

    def test_size(self):
        for log_size in range(1, 7):
            size = 10 ** log_size
            tmp_file = self.tmpdir.write('size/file_{0}'.format(size),
                                         bytearray(os.urandom(size)))

            self.assertEqual(ListDeletable.get_file_size(tmp_file), size,
                             'get_file_size is returning wrong value.')

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

    def test_deletions(self):
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

        with open(ListDeletable.config.DELETION_FILE, 'r') as deletions:
            for deleted in deletions.readlines():
                shutil.rmtree(ListDeletable.lfn_to_pfn(deleted.strip('\n')))

        for dir in all_dirs:
            check_file = self.tmpdir.getpath(os.path.join(dir, 'test_file.root'))
            self.assertEqual(os.path.exists(check_file), dir not in to_delete,
                             'File status is unexpected: %s' % check_file)

if __name__ == '__main__':
    unittest.main()
