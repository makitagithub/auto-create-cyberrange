# sandbox-creator

A next generation of https://gitlab.ics.muni.cz/KYPO-content/KYPO-Creator


generate.py is a python program that generates a vagrant source file from a definition in yaml. This yaml file contains definitions of devices (hosts and routers) and networks. Its structure is described below.

### Usage:
1. Clone the project.
2. Navigate to the project folder.
3. Type `$ python3 generate.py yaml_file.yaml`. There is a test yaml file in the repository called test.yaml.
4. Run `$ vagrant up`

### Input yaml file structure

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

### Testing the network

After a successful `vagrant up` it is sometimes needed to test the network routing:

1. Log in to a host with `$ vagrant ssh <host>`.
2. Ping a host from a different network with `$ ping <other-host>`.
3. If the networks are connected with a router and the routing works, ping gives an output (cca every second) about the transmitted packets. If ping cannot access the other host, no such output is produced.

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

### Implemented attribute types:
- all simple vagrant attributes
- flavors, memory, cpus
- a simple network (assigning ip and netmask to a device)
- simple routing (one router between networks)

### Not implemented yet:
- other VirtualBox attributes
- more complex routing

### Known [issues](https://gitlab.ics.muni.cz/cs4eu/sandbox-creator/issues):
- after running on Windows the output may contain invalid multibyte chars

### Notes
- tested on Vagrant 2.2.5, VirtualBox 6.0.4 and 6.0.10
- Vagrantfile and the provision directory contains everything needed by vagrant. Feel free to move them to a different directory after creation. 

### Other requirements
- DHCP server for vboxnet0 must be turned off in VirtualBox. It can be done manually in VirtualBox or with the command `$ VBoxManage dhcpserver remove --ifname vboxnet0`
