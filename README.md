# sandbox-creator

A next generation of https://gitlab.ics.muni.cz/KYPO-content/KYPO-Creator


generate.py is a python program that generates a vagrant source file from a definition in yaml.

### Usage:
1. Clone the project.
2. Navigate to the project folder.
3. Type `$ python generate.py {yaml_file.yaml} > Vagrantfile`. There is a test yaml file in the repository called test.yaml.
4. Run `$ vagrant up`

### Implemented attribute types:
- all simple vagrant attributes
- a simple network (assigning an ip address to a device)

### Not implemented yet:
- VirtualBox and OpenStack attributes
- other network configuration

