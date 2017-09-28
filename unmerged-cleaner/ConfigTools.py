# pylint: disable=protected-access, unexpected-keyword-arg

"""
This module includes tools for identifying the location of the unmerged directory
as well as generating the default configuration.

:author: Daniel Abercrombie <dabercro@mit.edu>
"""

import httplib
import socket
import ssl
import datetime
import os
import json


def pfn_from_phedex(site_name, lfn):
    """
    Get the PFN of a directory from phedex for a given LFN.

    :param str site_name: is the name of the site to check
    :param str lfn: is the LFN to find
    :returns: PFN of the folder
    :rtype: str
    """

    # Python 2.7.something verifies HTTPS connections,
    # but earlier version of Python do not
    try:
        conn = httplib.HTTPSConnection('cmsweb.cern.ch',
                                       context=ssl._create_unverified_context())
    except AttributeError:
        conn = httplib.HTTPSConnection('cmsweb.cern.ch')

    # Get the JSON from Phedex
    try:
        conn.request('GET',
                     '/phedex/datasvc/json/prod/lfn2pfn?'
                     'node=%s&protocol=direct&lfn=%s' %
                     (site_name, lfn))

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
    .. Todo:

       Get the host_map from SiteDB or someplace like that.

    :returns: Guessed site name for current location based on hostname
    :rtype: str
    """

    host = socket.getfqdn()

    #
    # Try mapping directly the domain for the LFN.
    # Feel free to add your domain here.
    #
    # If someone is feeling ambitious, they can try to do something clever with SiteDB.
    # If you create something fully automatic, please share it with Tools & Integration
    # because we know a number of people that will be interested.
    #

    host_map = {
        'oeaw.ac.at':     'T2_AT_Vienna',
        'iihe.ac.be':     'T2_BE_IIHE',
        'ucl.ac.be':      'T2_BE_UCL',
        'sprace.org.br':  'T2_BR_SPRACE',
        'cscs.ch':        'T2_CH_CSCS',
        'desy.de':        'T2_DE_DESY',
        'ciemat.es':      'T2_ES_CIEMAT',
        'ultralight.org': 'T2_US_Caltech',
        'ufl.edu':        'T2_US_Florida',
        'mit.edu':        'T2_US_MIT',
        'unl.edu':        'T2_US_Nebraska',
        'ucsd.edu':       'T2_US_UCSD'
        }

    for check, item in host_map.iteritems():
        if check in host:
            return item

    # Cannot find a possible site

    print 'Cannot determine site from this hostname.'
    print 'Feel free to edit the function ConfigTools.guess_site().'
    print 'For now, returning T2_US_MIT.'

    return 'T2_US_MIT'

#
# For developers: there are three steps to adding a properly documented configuration variable.
#
# 1. Make sure get_default(variable_name) returns a good default value for the variable.
#    This can be done by adding a default to the DEFAULTS dictionary, or by adding a special case
#    to the get_default() function.
# 2. Make sure the variable is documented inside the dictionary DOCS.
#    This will cause the documentation to show up in the default configuration generated
#    the first time ListDeletable.py is run and on our centrally maintained website.
# 3. Place the variable in the correct location in VAR_ORDER.
#    This is needed because some variables can depend on others,
#    so dependencies need to be declared first.
#    Let's not rely on dict.keys() for that.
#

# Default values for the configuration are given here:
DEFAULTS = {
    'LFN_TO_CLEAN':  '/store/unmerged',
    'STORAGE_TYPE':  'posix',
    'DIRS_TO_AVOID': ['SAM', 'logs'],
    'MIN_AGE':       60 * 60 * 24 * 7 * 2,    # Corresponds to two weeks
    'WHICH_LIST':    'directories',
    'SLEEP_TIME':    0.5,
}

DOCS = {
    'SITE_NAME':
        ('This is the site where the script is run at. The only thing this affects is the LFN\n'
         'to PFN translation of the unmerged directory, which can be overwritten directly using '
         '**UNMERGED_DIR_LOCATION**.'),
    'LFN_TO_CLEAN':
        ('The Unmerged Cleaner tool cleans the directory matching this LFN. On most sites, this\n'
         'will not need to be changed, but it is possible for a ``/store/dcachetests/unmerged``\n'
         'directory to exist, for example. The default is ``\'%s\'``.' % DEFAULTS['LFN_TO_CLEAN']),
    'UNMERGED_DIR_LOCATION':
        ('The location, or PFN, of the unmerged directory. This can be\n'
         'retrieved from Phedex (default) or given explicitly.'),
    'STORAGE_TYPE':
        ('This defines the storage type of the site. This may be necessary for the script to run\n'
         'correctly or optimally. Acceptable values are ``\'posix\'`` and ``\'hadoop\'``.\n'
         'The default is ``\'%s\'``.' % DEFAULTS['STORAGE_TYPE']),
    'DELETION_FILE':
        ('The list of directory or file PFNs to delete are placed this file.\n'
         'The default is ``\'/tmp/<WHICH_LIST>_to_delete.txt\'``.'),
    'DIRS_TO_AVOID':
        ('The directories in this list are left alone. Only the top level of directories within\n'
         'the unmerged location is checked against this if WHICH_LIST is ``\'directories\'``.\n'
         'The defaults are ``%s``.' % DEFAULTS['DIRS_TO_AVOID']),
    'MIN_AGE':
        ('Directories with an age less than this, in seconds, will not be deleted.\n'
         'The default (``%s``) corresponds to two weeks.\n'
         'Mathematical expressions here are evaluated.' % DEFAULTS['MIN_AGE']),
    'WHICH_LIST':
        ('Determines whether a list of directories or files will be generated.\n'
         'These lists will be in PFN format. Possible values are\n'
         '``\'directories\'`` or ``\'files\'``. '
         'The default is ``\'%s\'``.' % DEFAULTS['WHICH_LIST']),
    'SLEEP_TIME':
        ('This is the number of seconds between each deletion of a directory or file.\n'
         'The sleep avoids overloading the system and '
         'allows the operator to interrupt a deletion.\n'
         'The default is ``%s``.' % DEFAULTS['SLEEP_TIME']),
}

VAR_ORDER = [
    'SITE_NAME',
    'LFN_TO_CLEAN',
    'UNMERGED_DIR_LOCATION',
    'WHICH_LIST',
    'DELETION_FILE',
    'SLEEP_TIME',
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
        return 'UNMERGED_DIR_LOCATION = pfn_from_phedex(SITE_NAME, LFN_TO_CLEAN)'
    elif key == 'DELETION_FILE':
        return 'DELETION_FILE = \'/tmp/%s_to_delete.txt\' % WHICH_LIST'

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
                  '# %s on the node %s\n\n\n'
                  'from ConfigTools import pfn_from_phedex\n\n' %
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

                config_file.write('\n#' + '-' * 99 + '\n')
                config_file.write('# ' + DOCS[var].replace('\n', '\n# ').replace('``', '') + '\n\n')
                config_file.write(get_default(var) + '\n')
