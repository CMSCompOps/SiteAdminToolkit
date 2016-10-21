"""
This module includes tools for identifying the location of the unmerged directory
as well as generates the default configuration.

:author: Daniel Abercrombie <dabercro@mit.edu>
"""

import httplib
import socket
import ssl
import datetime
import os
import sys
import json


LFN = '/store/unmerged/'
"""
The LFN of the folder that the Unmerged Cleaner tool cleans.
"""


def unmerged_from_phedex(site_name):
    """
    Get the unmerged folder location from Phedex for a given site.

    If the site is given as 'test', the PFN returned will be
    two directories up from the script.
    If installed in the OpsSpace repository, this will land
    in the OpsSpace root.

    :param str site_name: is the name of the site to check
    :returns: PFN of the unmerged folder
    :rtype: str
    """

    # Return the OpsSpace directory for tests
    if site_name == 'test':
        return os.path.join(os.path.abspath('../..'))

    # Python 2.7 verifies HTTPS connections, but earlier version of Python do not
    if sys.version_info[:2] == (2, 7):
        conn = httplib.HTTPSConnection('cmsweb.cern.ch',
                                       context=ssl._create_unverified_context())
    else:
        conn = httplib.HTTPSConnection('cmsweb.cern.ch')

    # Get the JSON from Phedex
    try:
        conn.request('GET',
                     '/phedex/datasvc/json/prod/lfn2pfn?'
                     'node=%s&protocol=direct&lfn=%s' %
                     (site_name, LFN))

        res = conn.getresponse()
        result = json.loads(res.read())

    except Exception as msg:
        print 'Exception: %s' % msg
        print 'Failed to get LFNs from Phedex...'
        print 'Had tried %s.' % site_name
        conn.close()
        exit(1)

    location = result['phedex']['mapping'][0]['pfn']
    conn.close()
    return location


def guess_site():
    """
    :returns: Guessed site name for current location based on hostname
    :rtype: str
    """

    host = socket.gethostname()

    # Try mapping directly the domain to the LFN.
    # Feel free to add your domain here.

    unmerged_pfn_map = {
        'desy.de':        'T2_DE_DESY',
        'ultralight.org': 'T2_US_Caltech',
        'ufl.edu':        'T2_US_Florida',
        'mit.edu':        'T2_US_MIT',
        'unl.edu':        'T2_US_Nebraska',
        'ucsd.edu':       'T2_US_UCSD'
        }

    for check, item in unmerged_pfn_map.iteritems():
        if check in host:
            return item

    # Cannot find a possible unmerged location

    print 'Cannot determine site from this hostname.'
    print 'Feel free to edit the function ConfigTools.guess_site().'
    print 'For now, returning T2_US_MIT.'

    return 'T2_US_MIT'


# Default values for the configuration are given here:
DEFAULTS = {
    'STORAGE_TYPE': 'hadoop',
    'DELETION_FILE': '/tmp/files_to_delete.txt',
    'DIRS_TO_AVOID': ['SAM', 'logs'],
    'MIN_AGE':       60 * 60 * 24 * 7    # Corresponds to one week
}

DOCS = {
    'SITE_NAME': ('This is the site that the script is run at.\n'
                  'The only thing this affects is the location of the unmerged directory,\n'
                  'which can be overwritten directly.'),
    'UNMERGED_DIR_LOCATION': ('The location of the unmerged directory.\n'
                              'Can either be retrieved from Phedex (default) or given explicitly.'),
    'STORAGE_TYPE': ('This defines the storage type of the site.\n'
                     'This will be useful if there are future optimizations,\n'
                     'but is currently not used.\n'
                     'The default is ``\'%s\'``' % DEFAULTS['STORAGE_TYPE']),
    'DELETION_FILE': ('The list of directories to delete are placed in a file at this location.\n'
                      'The default is ``\'%s\'``' % DEFAULTS['DELETION_FILE']),
    'DIRS_TO_AVOID': ('This is a list of directories immediately inside unmerged to leave alone.\n'
                      'The defaults are ``%s``' % DEFAULTS['DIRS_TO_AVOID']),
    'MIN_AGE': ('Any directories with an age less than this, in seconds, will not be deleted.\n'
                'The default (``%s``) corresponds to one week.' % DEFAULTS['MIN_AGE'])
}

VAR_ORDER = [
    'SITE_NAME',
    'UNMERGED_DIR_LOCATION',
    'DELETION_FILE',
    'DIRS_TO_AVOID',
    'MIN_AGE',
    'STORAGE_TYPE',
    ]


def get_default(key):
    """
    :param str key: This can be any of the keys in DEFAULTS in addition to
                    SITE_NAME and UNMERGED_DIR_LOCATION
    :returns: a string to write to the default configuration module.
    :rtype: str
    """

    if key == 'SITE_NAME':
        return 'SITE_NAME = \'%s\'' % guess_site()
    elif key == 'UNMERGED_DIR_LOCATION':
        return 'UNMERGED_DIR_LOCATION = unmerged_from_phedex(SITE_NAME)'

    str_form = key + " = '%s'"
    if not isinstance(DEFAULTS[key], str):
        str_form = str_form.replace("'", '')

    return str_form % DEFAULTS[key]


def generate_default_config():
    """
    This generates the file ``config.py``, if it does not exist.
    Site admins should check this configuration and change to their desired
    values before running ``ListDeletable.py`` a second time.
    """

    if os.path.exists('config.py'):
        print 'Default config, config.py already exists.'
    else:

        # This goes at the top of the config file.
        header = ('# Automatically generated by ConfigTools.generate_default_config()\n'
                  '# %s on the node %s\n\n'
                  'from ConfigTools import unmerged_from_phedex\n\n' %
                  (datetime.date.strftime(
                      datetime.datetime.now(),
                      'On %d %B %Y at %H:%M:%S'
                      ),
                   socket.gethostname()
                  )
                 )

        with open('config.py', 'w') as config_file:
            config_file.write(header)

            # Order matters, so I put it by hand here.
            for var in VAR_ORDER:

                config_file.write('\n# ' + DOCS[var].replace('\n', '\n# ') + '\n')
                config_file.write(get_default(var) + '\n')
