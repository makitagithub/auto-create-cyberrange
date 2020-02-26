# sandbox-creator

A next generation of https://gitlab.ics.muni.cz/KYPO-content/KYPO-Creator

create.py is a python program that generates a vagrant source file from a definition in yaml. This yaml file contains definitions of devices (hosts and routers) and networks. Its structure is described below.


### Requirements:
- Python 3
- VirtualBox 6.0
- Ansible 2.3.3.0
- Vagrant 2.2.5


### Usage

#### 1. Preparing the host to be able to run virtual enviroments

##### Linux Mint

1. Enable [virtualization in BIOS](https://www.tactig.com/enable-intel-vt-x-amd-virtualization-pc-vmware-virtualbox/).
2. Install [VirtualBox 6.0](https://www.virtualbox.org/wiki/Download_Old_Builds_6_0).
3. Install Ansible with the command `$ sudo apt-get install ansible`.
4. Install [Vagrant](https://www.vagrantup.com/downloads.html).

##### Windows 10

1. Enable [virtualization in BIOS](https://www.tactig.com/enable-intel-vt-x-amd-virtualization-pc-vmware-virtualbox/).
2. Install [VirtualBox 6.0](https://www.virtualbox.org/wiki/Download_Old_Builds_6_0).
3. Install [Vagrant](https://www.vagrantup.com/downloads.html).

#### 2. Generating files using sandbox creator

##### Linux Mint

1. Install git using the command `$ sudo apt-get install git`.
2. Clone the project with `$ git clone https://gitlab.ics.muni.cz/cs4eu/sandbox-creator.git` to an arbitrary directory.
3. Navigate to the project directory (`$ cd sandbox-creator`).
4. Install pip using `$ sudo apt-get install python3-pip`.
5. Install setuptools with `$ pip3 install setuptools`.
6. Install dependencies with the command `$ pip3 install -r requirements.txt`.
1. Type `$ python3 create.py sandbox.yml`.[^1][^2]

##### Windows 10

1. Install [Python 3](https://www.python.org/downloads/windows/). At the beginning of the installation mark the "Add Python to PATH" option.
2. Install [git](https://git-scm.com/downloads).
3. Clone the project with `git clone https://gitlab.ics.muni.cz/cs4eu/sandbox-creator.git` to an arbitrary folder.
4. Navigate to the project folder (`$ cd sandbox-creator`).
5. Install Python dependencies using the command `python -m pip install -r .\requirements.txt`
6. Generate files using the command `python create.py -l sandbox.yml`.[^1][^2]

[^1]: This will rewrite the previously generated Vagrantfile and ansible files.
[^2]: The current version has a simple hardcoded recognition of network interfaces. This means, that in case of some topologies or boxes the name of the network interfaces is not recognized properly. See known issues for details.

#### 3. Creating and managing the virtual environment

- The command `$ vagrant up` builds the virtual environment. It must run from the same directory where the generated files are.
- `$ vagrant status` displays the created virtual machines and their state.
- The created virtual machines can be accessed with the command `$ vagrant ssh nameOfTheMachine`.
- The whole virtual environment can be destroyed using the command `$ vagrant destroy -f`.


### Known [issues](https://gitlab.ics.muni.cz/cs4eu/sandbox-creator/issues?scope=all&utf8=✓&state=all&label_name[]=known_issue)

- Sometimes the network interfaces are not recognized properly. the files generated from sandbox.yml at this stage needs a simple edit before running vagrant up. At the end of the file `base_provisioning/roles/routers/tasks/main.yml` the interface eth2 have to be changed to eth3 manually.
- After running on Windows the output may contain invalid multibyte chars.
- Check if DHCP server for vboxnet0 is turned off in VirtualBox. It can be done manually in VirtualBox or with the command `$ VBoxManage dhcpserver remove --ifname vboxnet0`
- Vagrant up can somtimes get stuck on "SSH auth method: private key" in case of "generic/debian10" box or on "SSH auth method: password" in case of "kalilinux/rolling-light" box. This is probably an issue of VirtualBox. In this case try to create the machine again. In case of "kalilinux/rolling-light" remove the line `device.ssh.password = "vagrant"` from the generated Vagrantfile and try to bring it up again.
- On some machines ansible local (flag -l) can get stuck while connecting to the created virtual machine.

#### Interface names and supported boxes

The name of the correct network interface can be different for every box. The supported boxes are listed in the file name_mappings/interface.yml. If your box is not on the list, the most common "eth1" will be used. If you get an error during `$ vagrant up` about non-existing network interface, you can add the name of your box and the correct network interface to the list manually.


### Notes
- tested on Vagrant 2.2.5, VirtualBox 6.0.4 and 6.0.10, Ansible 2.3.3.0
- Vagrant does not support VirtualBox 6.1 yet.
- Vagrantfile and the provision directory contains everything needed by vagrant. Feel free to move them to a different directory after creation. 


### Input yaml file structure

#### Basic attributes

- `hosts`: a list of host devices. All attributes of these virtual machines are defined here. Every host must have a unique `name` and a `base_box`.
	- `name`: unique name of the device (required)
	- `base_box`: an OS image that will be installed on the machine (required)
	- `cpus`: number of CPU units
	- `memory`: required memory size in MB
	- `flavor`: a quick definition of memory and cpus (details below)
	- other simple [vagrant attributes](https://www.vagrantup.com/docs/vagrantfile/machine_settings.html)

- `routers`: a list of routers. Routers need only a unique name. All other attributes are preset (Debian 10 with 256MB memory and 2 CPUs).
	- `name`: a unique router name (required)

- `networks`: list of networks
	- `name`: unique name of the network (required)
	- `cidr`: ip address of the network in cidr notation

- `net_mappings`: mappings of host machines to a network. This list defines the ip addresses of host in certain networks
	- `host`: name of an existing host
	- `network`: name of an existing network
	- `ip`: ip address of the host in the network

- `router_mappings`: similar to net_mappings. It defines the addresses of routers inside networks.
	- `router`: name of an existing router
	- `network`: name of an existing network
	- `ip`: ip address of the router in the network

#### Flavors

Flavors provide a quick way to choose hardware specs (like number of cpus and memory) for a virtual machine. These attributes can also be specified separately by `memory` and `cpus`. The values of `memory` and/or `cpus` always override the values specified in the `flavor`.

##### Supported flavors:
| flavor | cpus | memory |
| ------------------ |:--:|:-----:|
| csirtmu.tiny1x2    | 1  | 2048  |
| csirtmu.tiny1x4    | 1  | 4096  |
| csirtmu.small2x4   | 2  | 4096  |
| csirtmu.small2x8   | 2  | 8192  |
| csirtmu.medium4x8  | 4  | 8192  |
| csirtmu.medium4x16 | 4  | 16384 |
| csirtmu.large8x16  | 8  | 16384 |
| csirtmu.large8x32  | 8  | 32768 |
| csirtmu.jumbo16x32 | 16 | 32768 |
| csirtmu.jumbo16x64 | 16 | 65536 |



### Testing the network

After a successful `vagrant up` it is sometimes needed to test the network routing:

1. Log in to a host with `$ vagrant ssh <host>`.
2. Ping a host from a different network with `$ ping <other-host>`.
3. If the networks are connected with a router and the routing works, ping gives an output (cca every second) about the transmitted packets. If ping cannot access the other host, no such output is produced.

### Implemented attribute types:
- all simple vagrant attributes
- flavors, memory, cpus
- a simple network (assigning ip and netmask to a device)
- simple routing (one router between networks)

### Not implemented yet:
- other VirtualBox attributes
- more complex routing

### Credits

Cybersecurity laboratory\
Faculty of Informatics\
Masaryk University

Lead developer: Attila Farkas

Technology lead: Daniel Tovarňák (KYPO cyber range platform)

Supervisor: Jan Vykopal

Contributors:
*  Valdemar Švábenský
*  Michal Staník
*  Zdeněk Vydra
*  Adam Skrášek
