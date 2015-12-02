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


""" A Tool in SCons is a python module that (in its generate()) function modifies the Environment
so it can add Builders, and whatnot.

Usage (in SConscript):
env = Environment(tools=['pyff'], toolpath='<(relative) path to pyff.py>')
If the tool (i.e. pyff.py) is in one of the default tool locations recognised by SCons
toolpath can be omitted

Introduction to building tools: https://bitbucket.org/scons/scons/wiki/ToolsForFools
"""


from SCons.Script import *  # For PyCharm code completion
import SCons.Builder, SCons.Util

import re
import yaml
import hashlib
import os
import string


""" Build command for exececuting pyff
The pyff pipeline (.fd) file is generated from the parameters given to this function

source: The source XML metadata files to include. Accepted inputs:
        - String or Node  object: Single source
        - List of Strings / nodes: One or more sources
        - Dictionary: One or more sources: key is the selector that can be used in the select string, the value
                      is the name of the file
target: File to publish. String or Node.
select: String. XPath to use in select
remove: Optional. String or list of strings of EntityIDs to remove from the selection.
finalize: Optional. Tuple of (Name, cacheDuration, validUntil)

The order of the generated pipeline is:
- load: Load files specified in source
- select: Select entities by select XPath
- remove: Remove entities from selection by EntityID
- finalize: Set Name, cacheDuration and validUntil
- publish: Write metadata to target
"""
# Stand alone peudo builder
# Returns target nodes
def _pyff(env, source, target=[], select=None, remove=[], finalize=None) :

    target_node=env.File(target)
    source_nodes=None   # Make list of (Node, selecor)
    if SCons.Util.is_Dict(source):
        source_nodes=[ (env.File(source[s]), s) for s in source]
    elif SCons.Util.is_List(source):
        source_nodes=[ (env.File(s), None) for s in source]
    else:
        source_nodes=[ (env.File(source), None) ]
        source=[source]

    if not SCons.Util.is_List(remove):
        remove=[remove]

    # Generate fd file
    fd= '- load:\n'
    for s in source_nodes :
        fd+='  - ' + s[0].path
        if s[1]:
            fd+=' as ' + s[1]
        fd+='\n'
    if select:
        fd+='- select: "' + select + '"\n'
    if remove:
        fd+='- fork merge remove:\n'
        fd+='  - select:\n'
        for r in remove :
            fd+='    - ' + r + '\n'
    if finalize:
        fd+='- finalize:\n'
        fd+='    Name: ' + finalize[0] + '\n'
        fd+='    cacheDuration: ' + finalize[1] + '\n'
        fd+='    validUntil: ' + finalize[2] + '\n'
    fd+='- publish:\n'
    fd+='    output: ' + target_node.path + '\n'

    target_name = os.path.basename(target_node.path).translate(string.maketrans(' /\\', '___'))
    fd_filename = "pyff_" + target_name + '_' + hashlib.sha1(fd).hexdigest() + ".fd"
    fd_node = env.File( fd_filename )
    #env.AlwaysBuild(fd_node)

    def write_pyff_template(target, source, env) :
        with open(target[0].path, 'w') as f:
            f.write(fd) # fd is enclosed
        f.close()

    c1 = env.Command( target=fd_node, source=[ s[0] for s in source_nodes ], action=write_pyff_template)
    source_nodes.append( (fd_node, None) )
    env.Clean(c1, fd_node)

    # Note: pyff creates a .cache directory in current directory (i.e. the root dir, not the build dir)
    c2 = env.Command( target_node, [ s[0] for s in source_nodes ], ["$PYFF --loglevel=${PYFF_LOGLEVEL} "+fd_node.path] )

    return [ c1, c2 ]


""" Scan a pyff .fd file for sources (input files) and targets (files generated)
"""
def _pyff_emitter(target, source, env):
    target_add = set()
    source_add = set()

    # Match: "resource [as url] [[verify] verification] [via pipeline]"
    load_arg_re = re.compile('^\s*(?P<resource>\S+)(?:\s+as\s+\S+)?(?:\s+(?:verify\s+)?(?P<verification>\S+))?(?:\s+via\s+\S+)?\s*$', re.IGNORECASE)
    for fn in source:
        with open(fn.abspath, 'r') as stream:
            f = yaml.safe_load(stream)
            stream.close()

            def walk_pipe(d):
                for k,v in d.iteritems():
                    if k.strip().startswith('load'):
                        for arg in v:
                            m=load_arg_re.match(arg)
                            if (m != None):
                                r = m.group('resource')
                                if r.startswith('http://') or r.startswith('https://'):
                                    print "Warning: dynamic dowloaded resource '{0}' in '{1}'. Ignoring...".format(r, fn.path)
                                else:
                                    source_add.add(r)
                                #if 'verification' in m.groupdict().keys():
                                if m.group('verification') != None:
                                    print m.group('verification')
                                    source_add.add( m.group('verification') )
                            else:
                                raise Exception( "Parse error while scanning '{0}' for dependencies. Expected argument format 'load resource [as url] [[verify] verification] [via pipeline]', found '{1}'".format(fn.abspath, arg) )
                    elif k.strip().startswith('publish'):
                        if isinstance(v, str):
                            target_add.add(v)
                        elif isinstance(v, dict) and 'output' in v.keys():
                            target_add.add( v['output'] )
                        else:
                            raise Exception( "Parse error while scanning '{0}' for dependencies. Found 'publish', but could not determine output file".format(fn.abspath) )
                    elif k.strip().startswith('fork'):
                        # Fork start a new pipline
                        for i in v:
                            if isinstance(i, dict):
                                walk_pipe(i)
            for i in f:
                # Parse pipeline
                if isinstance(i, dict):
                    walk_pipe(i)
        print "Scanned '{0}': Discovered sources: {1}; targets: {2}".format(fn.abspath, list(source_add), list(target_add))

    return target + list(target_add), source + list(source_add)


# Test whether the file is signed with the specified certificate
# @param env environment object
# @param certificate PEM encoded certificate
# @param file XML file to check
#
# The "scripts/validatexmlsignature.sh" uses pyff to do the check
def _TestXMLSignature(env, certificate, file="${SOURCE}") :
    script_path=env.File('scripts/validatexmlsignature.sh').srcnode().path  # Get path before applying variant_dir with srcnode()
    certificate_path=env.File(certificate).path
    return {
        'action': SCons.Action.Action(script_path+" "+certificate_path+" ${SOURCE}"),
        'depends': certificate
    }

def _detect(env):
    pyff = env.WhereIs('pyff')
    if ('PYFF' in env):
        pyff = env['PYFF']
    else:
        print 'WARNING: pyff not found in path'
    return pyff

# Called by the Environment.Tools function
# Add ourselves to the environment
def generate( env ) :
    pyff = _detect(env)

    if pyff:
        env['ENV']['LANG'] = 'en_US.UTF-8' # Required for pyff to parse files as UTF-8
        env['ENV']['PYFF'] = env['PYFF'] = pyff

        env.AddMethod(_TestXMLSignature, "TestXMLSignature")
        env.AddMethod(_pyff, "pyff")


# Called during initialisation
# The tool can make it known whether it exists (i.e. is available)
def exists(env):
    return _detect()