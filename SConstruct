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

This SConstruct file takes care of the initialisation of the scons environment.
The actual build actions are defined in the included SConscript file
"""

from SCons.Script import *  # For PyCharm code completion
import os.path

Help("""
To build all targets, type: "scons"
To use a build directory, type: scons --build-dir=/tmp/build
To build a specific target, type: scons <name of target>
Note: The target must include the build dir specified using the --build-dir option. The '=' between
      options and values on the command line is required.
E.g. "scons --build-dir=/tmp/build /tmp/build/some-output.xml"

SConstruct specific (aka local) options:
--build-dir         Specify alternate build directory
--config-file       Specify configuration file, defaults to 'config.py'
--show-variables    Show the available variables with their current an default values
--fetch-metadata    Fetch remote metadata (default)
--no-fetch-metadata Do not fetch remote metadata

The config file is a python file that can contain any of the variables, variables can also be specified
at the scons command line. E.g. "scons --build-dir=build --no-fetch-metadata PYFF_LOGLEVEL=DEBUG"

Some usefull scons Options:
--clean            Remove generated files
--debug=explain    Explain why someting is build
--tree=all         Dump the dependency tree
""")

root_dir=Dir('#').abspath   # Root directory (i.e. the directory of this SConstruct)

AddOption('--build-dir', dest='build-dir', type='string', nargs=1, action='store', metavar='BUILDDIR',
          help='build directory',
          default=root_dir )
build_dir = GetOption('build-dir')   # The directory to build into

AddOption('--show-variables', dest='show-variables', action='store_true', default=False,
          help='Show the available build variables')

AddOption('--fetch-metadata', dest='fetch-metadata', action='store_true', default=True,
          help='Fetch remote metadata')
AddOption('--no-fetch-metadata', dest='fetch-metadata', action='store_false', default=True,
          help='Disable fetching of remote metadata')

AddOption('--config-file', dest='config-file', type='string', nargs=1, action='store', metavar='CONFIGFILE',
          help='configuration file',
          default='config.py' )
config_file = os.path.abspath( GetOption('config-file') )   # File containing variables

# Variables for setting system dependent configuration
# Variables can be specified in the "config.py "config file (use the --config-file option to specify
# an alternate file). The syntax of the file is python E.g.:
# PYFF='/opt/pyff/bin/pyff'
# Variables can also be specifed on the commandline directly. These will override those read from the
# configuration file. E.g.:
# scons --build-dir=build PYFF=/opt/pyff/bin/pyff
vars = Variables(config_file)
vars.Add('PYFF', 'Command to run pyFF')
vars.Add(EnumVariable('PYFF_LOGLEVEL', 'pyFF log level', 'INFO', allowed_values=('INFO', 'DEBUG')))
vars.Add('XMLSECTOOLSH', 'Command to run xmlsectool')
vars.Add('XMLSECTOOLSH_SIGN', 'Command to sign using xmlsectool')
vars.Add('XMLSECTOOLSH_KEYSTORE', 'JAVA keystore file to use when signing using xmlsectool')
vars.Add('XMLSECTOOLSH_KEYSTORE_KEY', 'Name of the key in the keystore to use when using xmlsectool')
vars.Add('XMLSECTOOLSH_KEYSTORE_PASSWORD', 'Password for the JAVA keystore', 'password')
vars.Add('XMLLINT', 'Command to run xmllint')
vars.Add('XSLTPROC', 'Command to run xsltproc')
vars.Add('JAVA_HOME', 'Path to the Java JRE')
vars.Add('FETCH_MD_COMMAND', 'Command that outputs federation metadata')
vars.Add('METADATA_VALID_UNTIL', 'Validity period for generated metadata', 'P10D')
vars.Add('METADATA_CACHE_DURATION', 'Cache duration for generated metadata', 'PT1H')

# Don't let SCons look for most of the buildin tools (e.g. C compiler). Explicitly list the ones
# we are interested in
DefaultEnvironment(tools = [
     'javah' # Detect JAVA_HOME
])

# Disable default handing of problems during value expansion
# Variable expansion: The replacement of $PYFF, $SOURCE, $TARGET etc by their actual values
# AllowSubstExceptions(NameError, IndexError)  # Default - ignore missing variables during expansion
AllowSubstExceptions() # Report all variable expansion problems

# Setup a build environment and add out own commands (tools) to it
env = Environment(
    variables=vars,
    toolpath=[root_dir + '/scons-tools'],   # Look for the tools in the "scons-tools" directory
    tools = [
        'URLDownload',  # Download a file using HTTP
        'pyff',         # Define and execute pyff pipelines
        'test',         # Test command and tests
        'xmlsectool'    # Execute xmlsectool
    ],
    URLDOWNLOAD_USEURLFILENAME=False,   # Make URLDownload tool use the target name we provide instead of the name in the URL
)

if 'JAVA_HOME' not in env['ENV']:
    env['ENV']['JAVA_HOME'] = env.subst('$JAVA_HOME')

if GetOption('show-variables'):
    print vars.GenerateHelpText(env)
    print "Exiting because of --show-variables option"
    exit(0)

# Unknown variables
if vars.UnknownVariables():
    print "Warning: Unrecognised variables on the command line: " + str(vars.UnknownVariables())

fetch_metadata = GetOption('fetch-metadata') # Whether to fetch / update metadata from external systems

download_dir=root_dir   # Directory to store downloaded files
if (build_dir != root_dir):
    build_dir=Dir(build_dir).abspath
    env.SConsignFile(build_dir+'/.sconsign.dblite') # Store the ".sconsign.dblite" file in the build directory instead of in the root_dir
    download_dir=root_dir+"/download/"+build_dir

env['DOWNLOAD_DIR'] = download_dir # Make the download dir available in the environment

# Dump environment that is being used for building in a way that can used from a shell
# That allows using the same environment when reproducing a build error
print 'Building from directory: %s' % root_dir
print 'Using build directory: %s'  % build_dir
print 'Reading configuration from: %s'  % config_file
print 'Using download directory: %s' % download_dir
print 'Fetch / update remote metadata: %s' % fetch_metadata
dict = env['ENV']
keys = dict.keys()
keys.sort()
exports=[]
for key in keys :
    exports.append( "export %s=%s" % (key, dict[key]) )
print 'Environment: ' + '; '.join(exports)

if len(COMMAND_LINE_TARGETS) > 0:
    print "Building target(s): " + ', '.join(COMMAND_LINE_TARGETS)
else:
    print "Building all targets"

## Include the "SConscript" and "SConscript.download" files that contains the build commands

if (build_dir != root_dir):
    SConscript( 'SConscript', exports='env', variant_dir=build_dir, duplicate=1 )
    Clean('.', build_dir) # Clean build dir as part of clean action (-c, --clean)
else:
    SConscript( 'SConscript', exports='env' )

# Because downloaded files will be removed from a variant_dir by scons, SConscript.downloads is not build in a
# variant_dir.
# All build commands (either in SConscript or SConscript.download) must use the "${DOWNLOAD_DIR}" from the env in
# targets and sources to refer to these files.
# Download commands should only have targets in DOWNLOAD_DIR
# Actions from the SConscript must not have targets in DOWNLOAD_DIR (only sources)
if fetch_metadata:
    SConscript( 'SConscript.download', exports='env')  # For downloading files into DOWNLOAD_DIR
