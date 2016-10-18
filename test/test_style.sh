#!/bin/bash

install=$1

# Check for pylint
if [ "`which pylint 2> /dev/null`" = "" ]
then

    # Full test is in virtualenv that needs pylint
    if [ "$install" = "install" -o "$TRAVIS" = "true" ]
    then

        pip install pylint

    else

        # Instruct on how to install, if not available
        echo "pylint not installed on this machine. Run:"
        echo ""
        echo "pip install pylint"
        echo ""
        echo "Or rerun this script as"
        echo ""
        echo "./test_style.sh install"
        echo ""
        exit 1

    fi

fi

# Save here, in case user is not in test dir
here=`pwd`

# Get the test dir
testdir=${0%%`basename $0`}
cd $testdir
testdir=`pwd`

# Set text output location
outputdir=$testdir"/pylint_output"
if [ ! -d $outputdir ]
then
    mkdir $outputdir
fi

# Get directory or package
opsdir=${testdir%%"/SiteAdminToolkit/test"}
cd $opsdir

# Define configuration for pylint
cfg26=test/pylint_py2.6.cfg
cfg27=test/pylint.cfg

if [ $(pylint --version 2> /dev/null | grep pylint | awk '{ print $2 }') = "1.3.1," ]
then

    sed 's/load-plugins=/#/g' $cfg27 > $cfg26
    pylintCall="pylint --rcfile $cfg26"

else

    pylintCall="pylint --rcfile $cfg27"

fi

# Cherrypy requires some things to be ignored for the class and cherrypy object
$pylintCall --disable=protected-access,unexpected-keyword-arg \
    SiteAdminToolkit/unmerged-cleaner/UnmergedCleaner.py > $outputdir/unmergedcleaner.txt

# Check the output
cd $testdir

ERRORSFOUND=0

for f in $outputdir/*.txt
do

    # Look for a perfect score
    if grep "Your code has been rated at 10" $f > /dev/null
    then

        tput setaf 2 2> /dev/null; echo $f" passed the check."

    else

        tput setaf 1 2> /dev/null; echo $f" failed the check:"

        if [ "$TRAVIS" = "true" ]    # For travis test, dump the output directly
        then
            tput sgr0 2> /dev/null
            cat $f
        else                         # Otherwise, show score and tell user to look
            tput setaf 1 2> /dev/null; cat $f | tail -n5
            tput setaf 1 2> /dev/null; echo "Check full file for more details."
        fi

        ERRORSFOUND=`expr $ERRORSFOUND + 1`

    fi

done

tput sgr0 2> /dev/null               # Reset terminal colors

cd $here                             # Return to original location

exit $ERRORSFOUND
