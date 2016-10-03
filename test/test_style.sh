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
pylintCall="pylint --rcfile test/pylint.cfg"

# Cherrypy requires some things to be ignored for the class and cherrypy object
$pylintCall SiteAdminToolkit/unmerged-cleaner/UnmergedCleaner.py > $outputdir/unmergedcleaner.txt

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
