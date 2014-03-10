#!/bin/bash

SITE="T2_US_Caltech"
REPLICAS=$(curl -X GET "https://cmsweb.cern.ch/phedex/datasvc/json/prod/filereplicas?lfn=$1" -k 2> /dev/null | sed 's/,/\n/g' | grep '\"node\":' | grep -v $SITE)

if [ -z "$REPLICAS" ] ; then
        echo "found no other replicas for $1"
else
        echo "found $1 in $REPLICAS"
fi

