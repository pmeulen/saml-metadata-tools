# Vagrant configuration file for development VM
# Should work with vmware fusion and virtual box providers

Vagrant.configure("2") do |config|

    # Note: The "nocm" version of the box doen not have any puppet software installed
    config.vm.box = "puppetlabs/ubuntu-14.04-64-nocm"

    config.vm.define "md-dev" do |app|
        app.vm.hostname = "md-dev"
        # Give it a fixed IP
        app.vm.network "private_network", ip: "192.168.66.12", :netmask => "255.255.255.0"
        app.vm.provider "vmware_fusion" do |v|
            v.vmx["memsize"] = "1536"
        end
        app.vm.provider "virtualbox" do |v|
            v.memory = 1536
        end
    end

    config.vm.provision "ansible" do |ansible|
        ansible.playbook = "provision.yml"
    #  #ansible.verbose = "vvvv"
    end

end