.. _site-admin-tool-ref:

Site Admin Toolkit
==================

|build|

This package contains useful tools for Site Admins to maintain their site.
These are generally scripts designed to be run from within the
directory they are stored after some configuration for a given site.

.. contents:: :local:
   :depth: 3

.. note::

  This documentation is new, so it does not describe all of the tools in ``SiteAdminToolkit`` repository.
  Anything that is frequently used should be added to the repository README to be useful to future admins.

.. _site-admin-tool-install-ref:

Installation
------------

Since the contents of this repository is currently scripts that do not depend on
the centralized :ref:`toolbox-ref`, installation can simply be done by cloning the repository::

    git clone https://github.com/CMSCompOps/SiteAdminToolkit.git

However, if you wish to run the test suites at your site,
you should install ``SiteAdminToolkit`` through the :ref:`OpsSpace installer <setup-ref>`.

.. _unmerged-ref:

Unmerged Cleaner
----------------

The Unmerged Cleaner tool is used to clean unprotected files from a site's unmerged directory.
This is usually the LFN ``/store/unmerged``.
Other possibilities exist, such as ``/store/dcachetests/unmerged``,
so this can be configured between separate runs, as described under :ref:`listdel-config-ref`.
There are three main steps to the deletion, which are also described in more detail later:

#. **Create a configuration file.**
   A default configuration file is created the very first time you run ``unmerged-cleaner/ListDeletable.py``.
   The script tries to import a ``config.py``.
   If it fails, ``config.py`` is generated.
   Make sure you do not have some existing ``config`` module that your Python installation will load instead.
   Then edit the variables described under :ref:`listdel-config-ref`.
#. **List the directories or files (configurable) inside the unmerged directory that can be deleted.**
   Directories that can be considered for deletion are ones that are not
   `listed as protected by Unified <https://cmst2.web.cern.ch/cmst2/unified/listProtectedLFN.txt>`_,
   are not too new (configurable), and are not in the ``logs`` or ``SAM`` directories (configurable).
   An optimized tool, :ref:`unmerged-list-ref`, has been created to do this step.
#. **Delete the directories.**
   After creating a list of directories or files that can be deleted, it is the admin's responsibility to remove them.
   Available tools are described under :ref:`unmerged-delete-ref`.
   Feel free to contribute scripts used for your own site by creating a pull request at the
   `CMSCompOps repository <https://github.com/CMSCompOps/SiteAdminToolkit>`_.

.. _unmerged-list-ref:

ListDeletable.py
~~~~~~~~~~~~~~~~

.. automodule:: ListDeletable

.. _unmerged-delete-ref:

Deletion Tools
~~~~~~~~~~~~~~

If you are going to use one of the available deletion tools on your site,
it is recommended that you run the unmerged cleaner unit test.

.. automodule:: test_unmerged_cleaner

Currently, there are two deletion tool available.
One is integrated into ``ListDeletable.py``,
and the other is a Perl script that is used on Hadoop systems.

ListDeletable.py --delete
+++++++++++++++++++++++++

``ListDeletable.py`` can be used to directly delete listed directories or files.

After creating and reviewing the list of directories or files to delete,
``ListDelete.py --delete`` reads your deletion file and removes the directories listed.
This is done via the :py:func:`ListDeletable.do_delete` function.
Please check the function documentation for any existing caveats.

This ``--delete`` flag will only work after the deletion file is created.
It is not possible to list and remove directories with an unmodified ``ListDeletable.py`` at the same time.
Any listed file or directory without ``/unmerged/`` in the path will cause the script to quit.

HadoopDelete.pl
+++++++++++++++

.. Warning::

   Currently untested. Serves as a template to be rewritten for a given site.

.. autoanysrc:: phony
   :src: ../SiteAdminToolkit/unmerged-cleaner/HadoopDelete.pl
   :analyzer: perl-script

.. _unmerged-ref-ref:

Unmerged Cleaner Reference
~~~~~~~~~~~~~~~~~~~~~~~~~~

Here are documented members of the :ref:`unmerged-ref`, mostly for people interested in adding some feature.

.. _umerged-list-ref-ref:

ListDeletable.py
++++++++++++++++

This documentation for ``ListDeletable`` does not have all members
because the module docstring is used to generate :ref:`unmerged-list-ref`.
This should be enough to get a contributor or advanced user started though.

.. autoclass:: ListDeletable.DataNode
   :members:

.. autofunction:: ListDeletable.do_delete

.. autofunction:: ListDeletable.filter_protected

.. autofunction:: ListDeletable.get_file_size

.. autofunction:: ListDeletable.get_mtime

.. autofunction:: ListDeletable.get_protected

.. autofunction:: ListDeletable.get_unmerged_files

.. autofunction:: ListDeletable.lfn_to_pfn

.. autofunction:: ListDeletable.list_folder

.. autofunction:: ListDeletable.main

.. _unmerged-config-ref-ref:

Config Tools Module
+++++++++++++++++++

The unmerged cleaner also makes use of the local module defined in ``ConfigTools.py``.

.. automodule:: ConfigTools
   :members:

SiteAdminToolkit Forks' Build Statuses
--------------------------------------

If you have a fork with automated build tests set up
(see :ref:`tests-ref`), then feel free to add your badge here for easy viewing.

dabercro: |build-dabercro|

.. |build-dabercro| image:: https://travis-ci.org/dabercro/SiteAdminToolkit.svg?branch=master
    :target: https://travis-ci.org/dabercro/SiteAdminToolkit

.. |build| image:: https://travis-ci.org/CMSCompOps/SiteAdminToolkit.svg?branch=master
    :target: https://travis-ci.org/CMSCompOps/SiteAdminToolkit
