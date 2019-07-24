#!/usr/bin/python3

import sys
import yaml
import jinja2

if (len(sys.argv) != 2):
    print ("Error: Expecting 1 argument (yml file).")
    sys.exit();

try:
    ymlfile = open(str(sys.argv[1]))
    yml = yaml.safe_load(ymlfile)
except IOError:
    print ("Error: file does not exist.")

try:
    v_mappings_file = open("name_mapping/vagrant.yml")
    vagrant_mappings = yaml.safe_load(v_mappings_file)
except IOError:
    print ("Error: cannot find mappings.")

# Converts yaml attribute names to vagrant attribute names.
def do_mapping(name, command_type):
    return vagrant_mappings[str(command_type)][name]

def add_formated_command(key, value):
    if (key in vagrant_mappings['string']):
        devices[host['name']].append('device.' + str(do_mapping(key, 'string')) + ' = \"' + str(value) + '\"')
    elif (key in vagrant_mappings['integer']):
        devices[host['name']].append('device.' + str(do_mapping(key, 'integer')) + ' = ' + str(value))
    elif (key in vagrant_mappings['boolean']):
        devices[host['name']].append('device.' + str(do_mapping(key, 'boolean')) + ' = ' + str(value).lower())

def find_ip(name):
    for net_mapping in yml['net_mappings']:
        if (net_mapping['host'] == name):
            return net_mapping['ip']

devices = {}

for host in yml['hosts']:
    devices[host['name']] = []
    for key, value in host.items():
        if (key != 'name'):
            add_formated_command(key, value)
    if (yml['net_mappings']):      
        devices[host['name']].append('device.vm.network :private_network, ip: \"' + str(find_ip(host['name'])) + '\"')

templateLoader = jinja2.FileSystemLoader(searchpath="templates")
templateEnv = jinja2.Environment(loader=templateLoader, trim_blocks=True)
baseTemplate = templateEnv.get_template("base")
output = baseTemplate.render(devices = devices)
print (output.encode('utf-8'))

#vagrantfile = open('Vagrantfile','w')
#vagrantfile.write(output)




