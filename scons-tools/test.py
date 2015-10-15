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

def _TestXMLWellFormedAction(env, file="${SOURCE}") :
    return { 'action': SCons.Action.Action("${XMLLINT} --noout --nonet " + file) }


# This is a pseudo-builder
# It creates a builder
# Like a builder it must return a list of node objects
def _test(env, target, source, tests = []) :
    actions = []
    for test in tests:
        actions.append(test['action'])
    actions.append( Copy(dest="$TARGET", src="$SOURCE") )

    nodes = []
    command = env.Command( target, source, actions )
    for test in tests:
        if 'depends' in test:
            Depends(command, test['depends'])

    nodes.append( command )

    return nodes

# generate function, that adds the builder to the environment,
# the value "DOWNLOAD_USEFILENAME" replaces the target name with
# the filename of the URL
# @param env environment object
def generate( env ) :
    xmllint = _detect(env)
    if xmllint:
        env['XMLLINT'] = xmllint
        env.AddMethod(_TestXMLWellFormedAction, "TestXMLWellFormed")

    env.AddMethod(_test, "Test")


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