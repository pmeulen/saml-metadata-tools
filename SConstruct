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

"""
SConstruct: The SCons equivalent of Makefile
Convention is to use the name "SConstruct" for the main file and to name files included
using SConscript() "SConscript"
"""

from SCons.Script import *  # For PyCharm code completion
import os.path

Help("""
To build all targets, just type: "scons"
To build a specific target, type: scons <name of target>
(Note: that target must include the build dir. E.g. "build/some-output.xml"

Some usefull Options:
--clean            Remove generated files
--debug=explain    Explain why someting is build
--tree=all         Dump the dependency tree
""")

# Don't let SCons look for most of the buildin tools (e.g. C compiler). Explicitly list the ones
# we are interested in
DefaultEnvironment(tools = [
    'javah' # Detect JAVA_HOME
])

# Setup a build environment and add out own commands to it
env = Environment(
    tools = ['URLDownload', 'pyff', 'test'],
    toolpath=['scons-tools'],
    PYFF='/opt/pyff/bin/pyff',
    #XMLLINT='path to xmllint'
)

# Make URLDownload tool use the target name we provide instead of the name in the URL
env['URLDOWNLOAD_USEURLFILENAME'] = False

# The directory to build into
build_dir="build"
# Make sure it exists
Mkdir(build_dir)

# Disable default handing of problems during value expansion
# Variable expansion: The replacement of $PYFF, $SOURCE, $TARGET etc by their actual values
# AllowSubstExceptions(NameError, IndexError)  # Default - ignore missing variables during expansion
AllowSubstExceptions() # Report all variable expansion problems


# Dump environment that is being used for building
# When reproducing an error, use the same environment
print "Building from directory: %s" % os.path.realpath(os.path.curdir)
print 'Using build directory: %s'  % os.path.realpath(build_dir)
dict = env['ENV']
keys = dict.keys()
keys.sort()
exports=[]
for key in keys :
    exports.append( "export %s=%s" % (key, dict[key]) )
print 'Environment: ' + '; '.join(exports)


SConscript( 'SConscript', exports='env', variant_dir=build_dir, duplicate=1 )