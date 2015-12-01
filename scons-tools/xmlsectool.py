import SCons.Action

def _detect(env) :
    if (not 'XMLSECTOOLSH' in env) :
        xmlsectool = env.WhereIs('xmlsectool.sh')
        if (xmlsectool) :
            env['XMLSECTOOLSH'] = xmlsectool

    return None

# @param target signed file (output)
# @param source file to sign (input)
# @param keystore path to java keystore (jsk) containing the signing key
# @param key name of key in keystore to use for signing
# @param keyPassword of the signing key
# @param digest Digest alogirthm to use in signature: SHA-1, SHA-256 or SHA-512

# xmlsectool.sh --sign --inFile in.xml --outFile out.xml --referenceIdAttributeName ID --digest SHA-256

def _Sign( env, target, source, keystore="$XMLSECTOOLSH_KEYSTORE", key="$XMLSECTOOLSH_KEYSTORE_KEY", keyPassword="$XMLSECTOOLSH_KEYSTORE_PASSWORD", digest='SHA=256'):
    command_str=""
    if 'XMLSECTOOLSH_SIGN' in env:
        command_str="${XMLSECTOOLSH_SIGN}"
    else:
        command_str="${XMLSECTOOLSH}"
    command_str += " --sign --inFile $SOURCE --outFile $TARGET --keystore %s --key %s --keyPassword %s" % (keystore, key, keyPassword)
    if 'XMLSECTOOLSH_SIGN_OPTS' in env:
        command_str+=" ${XMLSECTOOLSH_SIGN_OPTS}"
    return env.Command( target, source, command_str)

def generate( env ) :
    _detect(env)
    if 'XMLSECTOOLSH' in env :
        env.AddMethod( _Sign, "XML_Sign" )

# @param env environment object
# @return true
def exists(env) :
    _detect(env)
    return ('XMLSECTOOLSH' in env)