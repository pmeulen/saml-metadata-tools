# Set of tools for processing SAML metadata
 
The repository contains a work in progress. It the [SCons](http://www.scons.org) tools and "makefile" for 
generating RENATER metadata.

## SCons

Note: The SCons software is not deployed to the development VM yet. To run it in the development VM you
need to copy the files of this repo into it.

### Running it

Run `scons` to start the build. This command runs the `SConstruct` file.

The SConstruct takes care of the initialisation of scons build environment. The actual build rules are in the
`SConscript` file that it includes. Currently the build expects two files to be present:

1. cru-metadata.xml.in
2. renater-metadata.xml.in

These must be added manually.
