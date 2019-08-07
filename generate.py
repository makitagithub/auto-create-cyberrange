#!/usr/bin/python3

import sys
import yaml
import jinja2

from modules.network_parser import add_networks
from modules.provider import print_prov_attributes

if (len(sys.argv) != 2):
    print ("Error: Expecting 1 argument (yml file).")
    sys.exit();


# Loading external files
try:
    ymlfile = open(str(sys.argv[1]))
    yml = yaml.safe_load(ymlfile)
except IOError:
    print ("Error: file does not exist.")

try:
    mapping_file = open("name_mapping/mapping.yml")
    name_mappings = yaml.safe_load(mapping_file)
except IOError:
    print ("Error: cannot find mappings.")

try:
    flavors_file = open("name_mapping/flavors.yml")
    flavors = yaml.safe_load(flavors_file)
except IOError:
    print ("Error: cannot find the list of flavors.")


# Converts yaml attribute names to vagrant attribute names.
def do_mapping(name, command_type):
    return name_mappings[str(command_type)][name]

def add_formated_command(key, value):
    if (key in name_mappings['string']):
        devices[host['name']].append(
                'device.' + str(do_mapping(key, 'string'))
                + ' = \"' + str(value) + '\"')
    elif (key in name_mappings['integer']):
        devices[host['name']].append(
                'device.' + str(do_mapping(key, 'integer'))
                + ' = ' + str(value))
    elif (key in name_mappings['boolean']):
        devices[host['name']].append(
                'device.' + str(do_mapping(key, 'boolean'))
                + ' = ' + str(value).lower())


# Building "devices" structure that will be passed to Jinja2
devices = {}

for host in yml['hosts']:
    devices[host['name']] = []
    for key, value in host.items():
        if (key != 'name'):
            add_formated_command(key, value)
    add_networks(host['name'], yml, devices)
    print_prov_attributes(host, flavors
            , name_mappings['need_provider'], devices)


# Generating output via Jinja2
templateLoader = jinja2.FileSystemLoader(searchpath="templates")
templateEnv = jinja2.Environment(loader=templateLoader, trim_blocks=True)
baseTemplate = templateEnv.get_template("base")
output = baseTemplate.render(devices = devices)
print (output)

