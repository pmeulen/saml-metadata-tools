# Set of tools for processing, signing SAML metadata
 
The repository contains a work in progress. It uses the [SCons](http://www.scons.org) tools and "makefile" 
(SConstruct) for generating SAML 2 metadata for an identity federation.

The inluded tools are currently used at [RENATER](http://www.renater.fr). The SConstruct and some of the
scripts used are not yet published in this repo. We plan to add a generic working example of these later.

The included scons tools allow:

- Downloading (metadata) files from remote servers
- Running tests agins files:
  - XML Signature verification
  - XML syntac verification using xmllint
  - Verification using tests defined in an XSLT using 
- Dynammically generating and running [pyff](https://pythonhosted.org/pyFF/) pipeline (.py) files
- Signing using [xmlsectool](https://wiki.shibboleth.net/confluence/display/SHIB2/XmlSecTool)

## Required tools

The scons tools included in the project use several external tools. Below some notes on installing or getting these:
 
### pyFF

Note that the pyff tool uses pyff options in the "load" command that are not yet released. For a prebuild development 
version of pyff that included these features see: 
https://github.com/pmeulen/pyFF/releases/tag/0.10.0dev1-RENATER

More info on pyff can be found on the pyFF project page: https://pythonhosted.org/pyFF/

### xmlsectool

Download and install xmlsectool using the instruction at the projects page: 
https://wiki.shibboleth.net/confluence/display/SHIB2/XmlSecTool

### xmllint and xsltproc

The [xmllint](http://xmlsoft.org/) and [xsltproc](http://xmlsoft.org/XSLT/) included in a typical linux distribution 
should work fine.
