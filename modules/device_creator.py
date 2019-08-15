""" This package handles file import and creation of an input structure for
Jinja2 """

import yaml

from modules.attribute_formatter import add_simple_commands
from modules.provider import add_prov_attributes, add_router_specification
from modules.network_parser import add_networks, add_router_ip

MAPPING_FILE = "name_mapping/mapping.yml"
FLAVORS_FILE = "name_mapping/flavors.yml"


def _open_file(file_name):
    """ Opens and returns a file from the argument. """
    try:
        input_file = open(str(file_name))
        return yaml.safe_load(input_file)
    except IOError:
        print("Error: Cannot find a required file.")


def _create_hosts(yml, mappings, flavors):
    """ Creates a dictionary with formatted definition of each host. """
    host_definitions = {}

    for host in yml['hosts']:
        host_definitions[host['name']] = []

        add_simple_commands(host, mappings, host_definitions[host['name']])
        add_networks(host["name"], yml, host_definitions)
        add_prov_attributes(
            host, flavors, mappings['need_provider'], host_definitions)

    return host_definitions


def _create_routers(yml):
    """ Creates a dictionary with formatted definition of each router. """
    router_definitions = {}

    for router in yml['routers']:
        router_definitions[router['name']] = []
        add_router_ip(router["name"], yml, router_definitions)
        add_router_specification(router, router_definitions)

    return router_definitions


def create_devices(yml_file_name):
    """ Returns a merged dictionary of host and router definitions. """

    yml = _open_file(yml_file_name)
    mappings = _open_file(MAPPING_FILE)
    flavors = _open_file(FLAVORS_FILE)

    return {
        **_create_hosts(yml, mappings, flavors),
        **_create_routers(yml)}
