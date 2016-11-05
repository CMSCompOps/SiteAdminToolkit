#!/bin/bash
SITE="T2_US_Caltech"
PHEDEX_ROOT=$(echo "$PHEDEX_CONFIG_FILE" | awk -F"Config" '{print $1}')
echo "$PHEDEX_ROOT"

## WARNING : This is in dry-run mode (doesn't invalidate anything)
## To do that, uncomment the obvious line (test it before with a single file)

# shellcheck disable=SC2143
if [ -z "$("$PWD"/search-replicas.sh "$1" | grep "no other replica")" ] ; then

        echo "present in other locations than $SITE : $1 - INVALIDATING"
	echo "lfn:$1" > /tmp/invalidate-file.txt

	# FileDeleteTMDB is distributed in the GIT repository, not sure if it comes with PhEDEx (not in 4 series it seems) 
	# Recommendation : test it manually first
	#perl $PWD/FileDeleteTMDB --db /wntmp/phedex/info/DBParam.Site:Prod/YOURACCOUNTHERE -list /tmp/invalidate-file.txt -node T2_US_Caltech 
	# TODO: Add check of exit code from the above script (check that exit code makes sense). Log success/failure

else
        #echo "file is unique, report to transfers team : $1"
        echo "unique to $SITE : $1"
fi

rm -f /tmp/invalidate-file.txt
