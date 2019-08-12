import yaml

from .attribute_formatter import add_simple_commands
from .provider import add_prov_attributes, add_router_specification
from .network_parser import add_networks, add_router_ip


def _open_yml(yml_file_name):
    """ Opens the input yaml file. """
    try:
        ymlfile = open(str(yml_file_name))
        yml = yaml.safe_load(ymlfile)
        return yml
    except IOError:
        print ("Error: file does not exist.")


def _open_mappings():
    """ Opens the file with name mappings. """
    try:
        mapping_file = open("name_mapping/mapping.yml")
        mappings = yaml.safe_load(mapping_file)
        return mappings
    except IOError:
        print ("Error: cannot find mappings.")


def _open_flavors():
    """ Opens the file with flavor definitions. """
    try:
        flavors_file = open("name_mapping/flavors.yml")
        flavors = yaml.safe_load(flavors_file)
        return flavors
    except IOError:
        print ("Error: cannot find the list of flavors.")


def _create_hosts(yml, mappings, flavors):
    """ Creates a dictionary with formatted definition of each host. """
    host_definitions = {}

    for host in yml['hosts']:
        host_definitions[host['name']] = []
        
        add_simple_commands(host, mappings, host_definitions[host['name']])
        add_networks(host["name"], yml, host_definitions)
        add_prov_attributes(host, flavors
                , mappings['need_provider'], host_definitions)

    return host_definitions


def _create_routers(yml, mappings):
    """ Creates a dictionary with formatted definition of each router. """
    router_definitions = {}

    for router in yml['routers']:
        router_definitions[router['name']] = []
        add_router_ip(router["name"], yml, router_definitions)
        add_router_specification(router, router_definitions)

    return router_definitions


def create_devices(yml_file_name):
    """ Returns a marged dictionary of host and router definitions. """

    yml = _open_yml(yml_file_name)
    mappings = _open_mappings()
    flavors = _open_flavors()

    return dict(**_create_hosts(yml, mappings, flavors)
            , **_create_routers(yml, mappings))

