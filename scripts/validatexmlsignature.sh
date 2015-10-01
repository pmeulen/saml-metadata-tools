#!/bin/bash

PROGNAME=`basename $0`

# Wrapper around pyff
# Generates an fd file to verify the signature on a metadata file and executes pyff
# Usage: <certificate file> <metadata file to validate>

function error_exit
{
    echo "$PROGNAME: $1" 1>&2

    if [ -f "$TEMP_FD" ]; then
        rm $TEMP_FD
    fi
    exit 1
} 

if [ $# -ne 2 ]; then
    echo "Expected two arguments."
    echo "Usage: `basename $0` <certificate file> <metadata file to validate>"
    exit 1
fi

if [ -z "$PYFF" ]; then
    error_exit "PYFF not set"
fi 

TEMP_FD=`mktemp ${TMPDIR:-/tmp}/scons-fd.XXXXXXXXX`
if [ $? -ne 0 ]; then
    error_exit "mktemp failed"
fi

# Write .fd file 
cat << EOF > $TEMP_FD
- load:
   $2 verify $1
EOF

`$PYFF $TEMP_FD`
res=$?

rm $TEMP_FD

exit $res
