# sandbox-creator

A next generation of https://gitlab.ics.muni.cz/KYPO-content/KYPO-Creator


generate.py is a python program that generates a vagrant source file from a definition in yaml.

### Usage:
1. Clone the project.
2. Navigate to the project folder.
3. Type `$ python generate.py yaml_file.yaml`. There is a test yaml file in the repository called test.yaml.
4. Run `$ vagrant up`

### Implemented attribute types:
- all simple vagrant attributes
- flavors, memory, cpus
- a simple network (assigning ip and netmask to a device)

### Not implemented yet:
- VirtualBox and OpenStack attributes
- other network configuration

### Working yaml attributes
- hosts
    - all string, integer and boolean [vagrant attributes](https://www.vagrantup.com/docs/vagrantfile/machine_settings.html) (mappings of vagrant attribute names to yaml attributes are in name_mapping/mapping.yml)
    - flavor
    - memory
    - cpus
- networks
    - name
    - cidr
- net_mappings
    - host
    - network
    - ip
- routers
    - name
- router_mappings
    - router
    - network
    - ip

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

### Known [issues](https://gitlab.ics.muni.cz/cs4eu/sandbox-creator/issues):
- after running on Windows the output may contain invalid multibyte chars

### Notes
- tested on Vagrant 2.2.5, VirtualBox 6.0.4 and 6.0.10

