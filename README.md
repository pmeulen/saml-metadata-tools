# SCons metadata-tools

### A set of SCons tools for testing, processing and signing SAML metadata
 
The repository contains a work in progress. It uses the [SCons](http://www.scons.org) tools and "makefile" 
(SConstruct) to provide a framework that is aimed at generating SAML 2 metadata for an identity federation.

The included tools are currently used at [RENATER](http://www.renater.fr). The SConstruct and some of the scripts used
are not yet published in this repo. We plan to add a generic working example of these later.

The included SCons tools allow:

- Downloading (metadata) files from remote servers
- Running tests agains files:
  - XML Signature verification
  - XML syntac verification using xmllint
  - Verification using tests defined in an XSLT using 
- Dynammically generating and running [pyff](https://pythonhosted.org/pyFF/) pipeline (.py) files
- Signing using [xmlsectool](https://wiki.shibboleth.net/confluence/display/SHIB2/XmlSecTool)

The framework allows using a build directory that will contain all inputs and intermediate steps used in the build. 
This allows archival of a build and investigation of issues during a build. Individual steps, a whole build or only a
few (intermediate) targets can easily be rebuild. 

New tools or custom build step can easily be added.


# Required tools

The SCons tools included in the project use several external tools. Below some notes on installing or getting these:
 
## pyFF

The included pyFF tool dynamically generated pyFF pipelines. It targets pyFF 0.9.4.
More info on pyff can be found on the pyFF project page: https://pythonhosted.org/pyFF/

## xmlsectool

Download and install xmlsectool using the instruction at the projects page: 
https://wiki.shibboleth.net/confluence/display/SHIB2/XmlSecTool

## xmllint and xsltproc

The [xmllint](http://xmlsoft.org/) and [xsltproc](http://xmlsoft.org/XSLT/) included in a typical linux distribution should work fine.

## SCons

For runnning the SConscript [SCons](http://www.scons.org) is required. The version scons included in the typical linux 
distributions should work fine, although they are often quit out of date with the latest version from the scons website.


# Usage

This section deals with ussing SCons to run an already configured metadata-tools project.

To start a build:
* change to the metadata-tools directory;
* then use the ``scons`` command to start a build, adding the desired options (e.g. --build-dir=/tmp/build)

## Some usefull options

### Help
``scons --help`` show the included help with metadata-tools specific options and examples. To show the original SCons
 help for all the included options, execute the ``scons --help`` in a directory that does not inculde SConsctruct or 
 SConscript.

### Variables
``scons --show-variables`` shows the currently defined variables. Any variable can be given a new value by adding it 
to the command line: 
``scons --build-dir=/tmp/build --no-fetch-metadata PYFF_LOGLEVEL=debug``

### Build dir

Specifies where to put all the generated files. Downloaded files are also stored in this directory. Use 
``--build-dir`` option to specify it's location. Always use an "=" to prevent confusing the SCons commandline 
parser. E.g:
``scons --build-dir=/tmp/build``

### Do not download (metadata) files

Downloading files is enabled by default. To skip the downloading step add the ``--no-fetch-metadata``. E.g.:
``scons --build-dir=/tmp/build --no-fetch-metadata``

### Specify the target to build

To build only one target specify it in the command:
``scons --build-dir=/tmp/build --no-fetch-metadata /tmp/build/some-generated-file.xml``

When using abuild dir the build dir must be included in the target.

### Dependencies

SCons builds a complete tree of all dependencies the go into a build. It can be informative to see what the 
dependencies of a target are. The ``--tree=prune`` option can be used to show the dependency tree after a build. 
SCons keeps a very complete view of dependencies, including the SConstruct's, and tools used. This means that even 
the pruned tree can get quite big. It can be helpful to show the tree for single target:  
``scons --build-dir=/tmp/build --tree=prune /tmp/build/some-generated-file.xml``


# Troubleshooting a build

## Rerunning a command
The commands used to run the individual tools are output during the build. This allows rerunning of individual steps 
by simply rerunning the command from a commandline. For the most reliable results, ensure that the same same shell 
environment and user are used to execute the command.

Note that SCons sets it's own, minimal shell environment. The SCons output prints this environment at the start of 
the build. E.g.:
``Environment: export JAVA_HOME=/usr/lib/jvm/java-7-openjdk-amd64/; export LANG=en_US.UTF-8; export 
PATH=/usr/local/bin:/opt/bin:/bin:/usr/bin; ``...
To set this variable in your shell execute the line after "Environment:" in your shell.

## Rerunning a build

A build can be rerun by giving the same SCons command as that which was used to start the original build. SCons will 
only rebuild (intermediate) targets that are out of date (i.e. when a dependency was changed) or that are missing. To 
decide whether a file was changed SCons keeps track of the md5 checksum of the contents of the file. 

To prevent SCons from redownloading files the ``--no-fetch-metadata`` option can be added to the build command. E.g.:
``scons --build-dir=/tmp/build --no-fetch-metadata``
 
## Build order
 
The order in which files are build is decided by SCons, may vary between builds, and cannot be controlled. This means 
that rerunning a build may result in a different build order. SCons will respect dependencies so this should never be 
able to affect the actual result of the build. When a build terminated with an error, a change in build error could 
result in a different error.

## Building a single target

A single (intermediate) target can be rebuild by specifing the target on the commandline. This typically result in a 
shorter build, that is easier to troubleshoot. Note that the build directory must be added to the target. E.g:
``scons --build-dir=/tmp/build --no-fetch-metadata /tmp/build/some-generated-file.xml``


# Design

Provided in this repo is a SConscript. This SConscript initialises the SCons build environment (``env``) and adds the 
tools from the scons-tools directory to the environment. 

To add the actual build commands, a SConscript and SConscript.download must be added.

## SConscript.download

``SConscript.download`` is the first file that is included. The intention to put any build commands that download 
files in this SConscript. The SConscript add a ``DOWNLOAD_DIR`` variable to the build environment. Any downloaded 
content should be stored there.
 
The execution of the ``SConscript.download`` is controlled by the ``--fetch-metadata`` and ``--no-fetch-metadata`` 
options. This allows reproducing a build with pereviously downloaded files by adding the ``--fetch-metadata``.

## SConscript

Finally the ``SConscript`` is included. All the other build commands should be put in this file.  

## Build directory

The ``--build-dir`` option can be used to perform the build in another directory than the current. This uses the 
SCons variant_dir functionality to execute the SConscript in this directory. The ``DOWNLOAD_DIR`` is a subdirectory 
of the build-dir. Also the SCons database is stored in the build-dir. This means that all files related to the build 
are stored in the build directory.  

When using a build directory nothing is written to the metadata-tools directory (where the main SConscript file is 
stored). There is one exception: pyFF needs a .cache directory in this directory, but since there is no need for pyff
 to download any files, nothing will be actually written to this directory.
 
Thus the build directory (and the metadata-tools) are all that is required to repoduce a build or repeat individual 
steps from the build process.

The target(s) to build can be specified to SCons. Note that targets must include the build-dir path.

## config.py
 
Several metadata-tools specific variables are available. Use ``scons --show-variables`` to get a full list of the 
variables, their current value and description. Variables can be specified to scons on the commandline (e.g. 
``scons PYFF_LOGLEVEL=debug``). On startup variables are read from a ``config.py`` file in the metadata-tools 
directory when present. Variables for SCons on the commandline override those given in the config.py file. 

Example config.py file:
```
XMLSECTOOLSH='/opt/xmlsectool/xmlsectool.sh'
XMLSECTOOLSH_KEYSTORE='md-signing.jks'
XMLSECTOOLSH_KEYSTORE_KEY='md-signing'
XMLSECTOOLSH_KEYSTORE_PASSWORD='password'
PYFF='/opt/pyff/bin/pyff'
#JAVA_HOME='/Library/Java/JavaVirtualMachines/jdk1.8.0_65.jdk/Contents/Home'
JAVA_HOME='/usr/lib/jvm/java-7-openjdk-amd64/'
FETCH_MD_COMMAND='cat'
PUSH_MD_COMMAND='cp'
```

The included tools will try to autodetected locations of the tools like pyff, xsltproc or xmllint if these are not 
provides in the config.py or on the command line.  

