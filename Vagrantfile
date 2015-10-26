# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|

  config.vm.box = "https://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"
  config.vm.hostname = "art-reports.linaro.org"
  config.vm.network "private_network", ip: "10.0.0.100"
  config.vm.define "art-reports.linaro.org" do |artreports|
  end

  config.vm.provider "virtualbox" do |v|
    v.memory = 3024
    v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    v.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
  end

   config.vm.synced_folder ".", "/vagrant", type: "nfs"

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "ansible/site.yml"
  end
end
