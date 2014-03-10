# Gums Remap/Recylce Users

## Problem

The Department of Energy (DOE) informed the Open Science Grid (OSG) that they
would no longer provide a Certificate Authority (CA) service.  OSG performed
a search and decided to contract with DigiCert to provide personal and host
certificates.  This meant that all users would receive new personal 
certificates once their old DOE certificates expired.  GUMS does user mapping
based on the proxy that the user generates from their personal certificate.
Additionally, data access is controlled via the usernames that GUMS maps users
to.  This means that a mechanism to ensure that the users retain their original
mappings with the new certificates is required.

## Solution

The remap-user-recycle script provides a way to directly manipulate the GUMS
database to remap a users new certificate to their original username mapping.

The script has quite a few other options as well.  See the help for full 
documentation.

## Authors

Principle Author:  John Weigand
Contributions:
    Bockjoo Kim