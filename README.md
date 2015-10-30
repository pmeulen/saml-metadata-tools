Set of tools for processing SAML metadata
=========================================
 
The repository contains a work in progress. It contains three things that are releated:

* [SCons](http://www.scons.org) tools and "makefile" for generating RENATER metadata
* [Vagrant](https://www.vagrantup.com/) configuration for creating developement VMs
* [Ansible](http://ansible.com) scripts for setting up the (development) servers


Deploying developement VMs
--------------------------

* Install [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org). Virtualbox will run 
  the development VMs, Vagrant is used to create and configure and manage the instances.
* Install [Ansible](http://www.ansible.com). There are several ways to install Ansible. They are described in the 
  [installation guide](http://docs.ansible.com/ansible/intro_installation.html).

To create and start the development VMs use `vagrant up`. To addess a single VM, add its name to the vagrant command. 
E.g. `vagrant up dev-md`. To ssh into a VM type `vagrant ssh dev-md`.

The last step of creating a VM is to run the `provision.yml` Ansible script. This scripts makes some configuration 
changes to the VM. Vagrant is configured to run this script automatically. To rerun the provision step manually use 
`vagrant provision`.

Ansible
-------

The Ansible environment (i.e. the configuration specific to a set of servers like IP addesses and passwords) for the 
development VMs is stored in the `ansible/dev-environment` directory. The idea is to have an environment for each set 
of servers (i.e. testing, staging, production, ...). 

During provisioning Vagrant creates an "inventory" file for use by Ansible. This inventory is linked to from the 
dev-environment so all ssh keys, IPs are already set. This is convenient for development. For other environments the 
inventory could be created manually or generated by other tools.

A script is provided to generate SSL certificates for the environment. To run the script for the dev-environemnt:
`ansible/scripts/create_new_environment.sh ansible/dev-environment`
This currently just adds the two certificates to the ansible/dev-environment directory that are required for the deploy by Ansible. By changing the configuration in "ansible/scripts/environemnt.conf" the can do more.

To start an Ansible deploy to the development VMs run: 
`ansible-playbook ansible/site.yml -i ansible/dev-environment/inventory`

You can "limit" which servers Ansible deploys. E.g. to deploy only the "md-dev" server:
`ansible-playbook ansible/site.yml -i ansible/dev-environment/inventory -l md-dev`

### About "host_ipv4" ###

For each server an Ansible `host_ipv4` must is set in the environment. Although Ansible can dynamically discover 
"facts" of servers (including IP adesses) and have these available for use in scripts, this "dynamic" can also cause 
issues during depoyments when not all servers are reachable to discover the facts. This is why I prefer to provide 
this info statically in the Ansible environment.


SCons
-----

Note: The SCons software is not deployed to the development VM yet. To run it in the development VM ssh into it
(`vagrant ssh md-dev`) and change to the `/vagrant` directory.

Run `scons` to start the build. This command runs the `SConstruct` file.

The SConstruct takes care of the initialisation of scons build environment. The actual build rules are in the
`SConscript` file that it includes. Currently the build expects two files to be present:

1. cru-metadata.xml.in
2. renater-metadata.xml.in

These must be added manually.