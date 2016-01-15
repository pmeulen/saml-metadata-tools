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
This function supports a subset of the pyff functionality, it is not a full replacement for a full custom pyff pipeline

source:  The source SAML 2.0 XML metadata file(s) to include. Note that a source should be a file on disk.
         A metadata file can have an EntityDescriptor or an EntitiesDescriptor as root element
         When sthe same EntityID occurs in multiple files the order of the source files decides which EntityDescriptor
         will be included in the output. Entities from the first source file listed take precedence over entities in the
         second source file, which take precedence over those listed in the third etc.
         Accepted inputs:
         - String or Node object: A single source file is loaded
         - List of Strings / nodes: All the sources in the list are loaded
         - Dictionary of key => source: All the sources in the dictionary are loaded: The "key" can be used is the
           select string
target:  Output file. String or Node.
select:  Optional. String or list of strings of XPaths to select the EntityDescriptors to output. When left blank all the
         entities in the source file(s) are selected for output.
         A select statement takes the form: "<key>!<xpath expression>"
         Examples:
         "!//md:EntityDescriptor[md:IDPSSODescriptor]" - select all entities that contain an IDPSSODescriptor
         "SOURCE_1!//md:EntityDescriptor" - select all entities from the file loaded with key "SOURCE_1"
         "SOURCE_0" - select all entities loaded with key "SOURCE_0"
remove:  Optional. String or list of strings of EntityIDs to remove from the selection.
finalize: Optional. Tuple of attributes to set on the SAML 2.0 EntitiesDescriptor (Name, cacheDuration, validUntil)
          - Name: String identifying this metadata (URI)
          - cacheDuration: Recommended cache duration for clients. XML timedelta expression. E.g. cache for one hour: PT1H
          - validUntil: Expiry date. ISO 8601 time string or XML timedelta expression. E.g. valid for 6 days starting
             now: PT6D
xslt:    Optional. String or Node object. The xslt stylesheet to apply to the output

The order of the generated pipeline is:
- load: Load the file(s) specified in source. This makes these files available for selection
- select: Select entities by select XPath. If no select is provided all loaded entities are selected.
- remove: Remove entities from selection by EntityID
- finalize: Set Name, cacheDuration and validUntil
- xslt: Apply XSLT stylesheet
- publish: Write metadata to target
"""
# Stand alone peudo builder
# Returns target nodes
def _pyff(env, source, target=[], select=None, remove=[], finalize=None, xslt=None) :

    target_node=env.File(target)
    source_nodes=None   # Make list of (Node, selecor)
    if SCons.Util.is_Dict(source):
        source_nodes=[ (env.File(source[s]), s) for s in source]
    elif SCons.Util.is_List(source):
        source_nodes=[ (env.File(s[1]), "SOURCE_%s" % s[0]) for s in enumerate(source)]
    else:
        source_nodes=[ (env.File(source), "SOURCE_0") ]

    if not SCons.Util.is_List(remove):
        remove=[remove]

    if select and not SCons.Util.is_List(select):
        select=[select]

    ## Generate the fd file for pyff
    # Load
    fd= '- load max_workers 1 timeout 10 validate True fail_on_error True filter_invalid False:\n'
    for s in source_nodes :
        fd+='  - ' + s[0].path +' as ' + s[1]
        fd+='\n'

    # Select
    if select:
        fd+='- select:\n'
        for s in select :
            fd+='  - "' + env.subst(s) + '"\n'
    else:
        fd+='- select\n'

    # Make earlier of loaded sources take priority over later loaded ones.
    # A "fork merge replace_existing" will replace each EntityDescriptor in the main branch that also exists in the fork
    # by that from the fork. Comperison of EntityDescriptors is done by EntityID
    if len(source_nodes) > 1:
        for s in reversed(source_nodes[0:-1]):  # iterate over sources from N-1 to 0.
            fd+="- fork merge replace_existing:\n"
            fd+="  - select: " + s[1] + "\n"

    if remove:
        fd+='- fork merge remove:\n'
        fd+='  - select:\n'
        for r in remove :
            fd+='    - ' + env.subst(r) + '\n'

    if finalize:
        if len(finalize) < 3:
            raise ValueError('pyff: finalize argument requires tuple of (Name, cacheDuration, validUntil)')

        fd+='- finalize:\n'
        fd+='    Name: ' + env.subst(finalize[0]) + '\n'
        fd+='    cacheDuration: ' + env.subst(finalize[1]) + '\n'
        fd+='    validUntil: ' + env.subst(finalize[2]) + '\n'

    xslt_node=None
    if xslt:
        xslt_node=env.File(xslt)
        fd+='- xslt:\n'
        fd+='    stylesheet: ' + xslt_node.path + '\n'

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
    if xslt_node:
        env.Depends(c2, xslt_node)

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
# Test action for use with the "Test" builder
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