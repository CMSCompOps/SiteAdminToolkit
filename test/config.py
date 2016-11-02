# Testing configuration

import os
import sys

from ConfigTools import pfn_from_phedex

SITE_NAME = 'test'
LFN_TO_CLEAN = '/store/unmerged'
DELETION_FILE =  'unmerged_results/to_delete.txt'
DIRS_TO_AVOID = ['avoid']
MIN_AGE = 5

if len(sys.argv) > 1:
    UNMERGED_DIR_LOCATION = os.path.abspath(sys.argv.pop(1))
else:
    UNMERGED_DIR_LOCATION = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'unmerged')

if len(sys.argv) == 1:
    sys.argv.append('test')

STORAGE_TYPE = sys.argv.pop(1)
WHICH_LIST = 'directories'
