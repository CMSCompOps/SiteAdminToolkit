#!/bin/bash
SUCCESSES=$(grep "ended with rc" /var/log/gridftp-auth.log   | tail -n100 | awk '{print $13 $15}' | sort | uniq -c | grep rc0 | awk '{print $1}')
RATE=$(echo "scale=2; ($SUCCESSES/100)*100" | bc)
echo $RATE
