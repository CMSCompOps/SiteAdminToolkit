Site Admin Toolkit
==================

|build|

This package contains useful tools for Site Admins to maintain their site.
These are generally Python or Perl scripts designed to be run from within the
directory they are stored after some configuration for a given site.

.. contents:: :local:

.. note::

  This documentation is new, so it does not describe all of the tools in this repository.
  Anything that is frequently used should be added to the repository README.

Installation
------------

Since the contents of this repository is currently scripts that do not depend on
the centralized :ref:`toolbox-ref`, installation can simply be done by cloning the repository::

    git clone https://github.com/CMSCompOps/SiteAdminToolkit.git

Installation of the Site Admin Toolkit has also been enabled under the general :ref:`OpsSpace installer <setup-ref>`.

Unmerged Cleaner
----------------

The Unmerged Cleaner tool is used to clean unprotected files from a site's ``/store/unmerged`` directory.
There are two steps to this:

#. **List the directories inside /store/unmerged that can be deleted.**
   Directories that can be considered for deletion are ones that are not
   `listed as protected by Unified <https://cmst2.web.cern.ch/cmst2/unified/listProtectedLFN.txt>`_,
   are not too new (configurable), and are not in the ``logs`` or ``SAM`` directories (configurable).
   An optimized tool, :ref:`unmerged-list-ref`, has been created to to this step.
   See that section for more directions.
#. **Delete the directories.**
   After creating a list of directories that can be deleted,
   it is the admin's responsibility to remove them.
   Available tools are described under :ref:`unmerged-delete-ref`.
   Feel free to contribute scripts used for your own site
   by creating a pull request at the 
   `CMSCompOps repository <https://github.com/CMSCompOps/SiteAdminToolkit>`_.
   Contributers are encouraged to follow :ref:`developer-ref`.   

.. _unmerged-list-ref:

ListDeletable.py
~~~~~~~~~~~~~~~~

.. automodule:: ListDeletable
   :members:

.. _unmerged-config-tools-ref:

Config Tools Module
~~~~~~~~~~~~~~~~~~~

The unmerged cleaner also makes use of the local module defined in ``ConfigTools.py``.
This is documented for reference purposes.

.. automodule:: ConfigTools
   :members:

.. _unmerged-delete-ref:

Deletion Tools
~~~~~~~~~~~~~~

Currently, there is only one deletion tool available.
This is a Perl script that is used on Hadoop systems.

HadoopDelete.pl
+++++++++++++++

.. autoanysrc:: phony
   :src: ../SiteAdminToolkit/unmerged-cleaner/HadoopDelete.pl
   :analyzer: shell-script

SiteAdminToolkit Forks' Build Statuses
--------------------------------------

If you have a fork with automated build tests set up
(see :ref:`tests-ref`), then feel free to add your badge here for easy viewing.

dabercro: |build-dabercro|

.. |build-dabercro| image:: https://travis-ci.org/dabercro/SiteAdminToolkit.svg?branch=master
    :target: https://travis-ci.org/dabercro/SiteAdminToolkit

.. |build| image:: https://travis-ci.org/CMSCompOps/SiteAdminToolkit.svg?branch=master
    :target: https://travis-ci.org/CMSCompOps/SiteAdminToolkit
