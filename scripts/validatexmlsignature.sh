#!/bin/bash

# Copyright 2015 GIP RENATER
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Wrapper around pyff
# Generates an fd file to verify the signature on a metadata file and executes pyff
#
# The PYFF environment variable must be set to the path of pyff. E.g.
#   PYFF=/opt/pyff/bin/pyff
#
# Usage: <certificate file> <metadata file to validate>
#
# Return 0 on sucess, nonzero value otherwise.

PROGNAME=`basename $0`

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
   - $2 as dummy verify $1
EOF

echo `$PYFF $TEMP_FD`
res=$?

if [ $res -ne 0 ]; then
    echo "Failed executing pipeleine:"
    cat $TEMP_FD
fi

rm $TEMP_FD

exit $res
