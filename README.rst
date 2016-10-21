Site Admin Toolkit
==================

|build|

This package contains tools for Site Admins to maintain their site.

.. note::

  This documentation is new, so it does not describe all of the tools in this repository.
  Anything that is frequently used should be added to the repository README.

Unmerged Cleaner
----------------

This tool is used to clean unprotected files from a site's :file:`unmerged` directory.
This is done by running :file:`UnmergedCleaner.py`.

UnmergedCleaner.py
~~~~~~~~~~~~~~~~~~

.. automodule:: UnmergedCleaner
   :members:

Config Tools Module
~~~~~~~~~~~~~~~~~~~

The unmerged cleaner also makes use of the local module Config Tools.
This is documented below.

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
