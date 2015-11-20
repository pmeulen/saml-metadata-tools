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

import urllib2, urlparse
import SCons.Builder, SCons.Node.FS, SCons.Errors, SCons.Action
from SCons.Script import *


# This is a pseudo-builder, it generates a build command
# Like a builder it returns a list of target node objects

# This builder creates a command from the actions provided in "tests"
# Each test is an action
# The final action copies the file. This way:
# - All tests must be succeed before the file is copied
# - The tests are only run when the source files changed

# @param env environment object
# @param target target node
# @param source target node
# @param tests list of tests
#
# A test is an dict: { 'action': SCons.Action, 'depends': (list of) Node/filenames }
# - action is mandatory and is the action that executes the test
# - depends is optional. It can be used to add additional dependencies to the test
def _test(env, target, source, tests = []) :
    actions = []
    for test in tests:
        actions.append( test['action'] )
    actions.append( Copy(dest="$TARGET", src="$SOURCE") )

    nodes = []
    command = env.Command( target, source, actions )
    for test in tests:
        if 'depends' in test:
            Depends(command, test['depends'])

    nodes.append( command )

    return nodes


# Test an XML file for well formedness
# @param env environment object
# @param file file to test
def _TestXMLWellFormedAction(env, file="${SOURCE}") :
    return { 'action': SCons.Action.Action("${XMLLINT} --noout --nonet " + file) }


# generate function, that adds the builder to the environment,
# the value "DOWNLOAD_USEFILENAME" replaces the target name with
# the filename of the URL
# @param env environment object
def generate( env ) :

    # Add the "Test" command to the environment
    env.AddMethod(_test, "Test")

    xmllint = _detect(env)
    if xmllint:
        env['XMLLINT'] = xmllint
        env.AddMethod(_TestXMLWellFormedAction, "TestXMLWellFormed")


def _detect(env) :
    xmllint = env.WhereIs('xmllint')
    if ('XMLLINT' in env) :
        xmllint = env['XMLLINT']

    return xmllint

# existing function of the builder
# @param env environment object
# @return true
def exists(env) :
    return 1