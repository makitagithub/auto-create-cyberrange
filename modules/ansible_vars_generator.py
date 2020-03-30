from modules.file_manager import generate_file, dump_to_yaml
from conf.border_router import BORDER_ROUTER_NETWORK_NAME


def _find_networks_of_device(name, input_definitions):
    """ Returns a list of network names in which the device have an
    interface.
    """

    networks = []
    
    for net_mapping in input_definitions["net_mappings"]:
        if net_mapping["host"] == name:
            networks.append(net_mapping["network"])
    
    if len(networks) == 1:
        return networks

    if len(networks) > 1:
        print("Error: Hosts can have only one interface.")
        raise AttributeError

    for router_mapping in input_definitions["router_mappings"]:
        if router_mapping["router"] == name:
            networks.append(router_mapping["network"])

    return networks
        

def _add_aliases(device_name, input_definitions, flags):
    """ Generates aliases for the given device. """

    home_networks = _find_networks_of_device(device_name, input_definitions)

    aliases = dict()

    for host_mapping in input_definitions["net_mappings"]:
        aliases[host_mapping["host"]] = host_mapping["ip"]
        continue

    for router_mapping in input_definitions["router_mappings"]:
        if router_mapping["network"] in home_networks:
            aliases[router_mapping["router"]] = router_mapping["ip"]
            continue

    for router in input_definitions["routers"]:
        if router["name"] not in aliases:
            if "border_router" not in flags:
                print("Error: " + device_name + " has no connection to " + router["name"] + " .")
                raise AttributeError
            for router_mapping in input_definitions["router_mappings"]:
                if router_mapping["router"] == router["name"] and router_mapping["network"] == BORDER_ROUTER_NETWORK_NAME:
                    aliases[router_mapping["router"]] = router_mapping["ip"]
                    continue
            
    for router in input_definitions["routers"]:
        if router["name"] not in aliases:
            print("Error: " + device_name + " has no connection to " + router["name"] + " .")
            raise AttributeError

    return aliases
            

def _generate_device_vars(input_definitions, flags):
    """ Generates vars files for all devices separately. """

    for target_host in input_definitions["hosts"]:
        variables = dict()
        variables["aliases"] = _add_aliases(target_host["name"], input_definitions, flags)
        dump_to_yaml(variables, "base_provisioning/roles/" + target_host["name"] + "/vars/main.yml")

    for target_router in input_definitions["routers"]:
        variables = dict()
        variables["aliases"] = _add_aliases(target_router["name"], input_definitions, flags)
        dump_to_yaml(variables, "base_provisioning/roles/" + target_router["name"] + "/vars/main.yml")


def _generate_hosts_vars(input_definitions, flags):
    """ Generates vars file for all hosts. """

    return


def _generate_routers_vars(input_definitions, flags):
    """ Generates vars file for all routers. """

    return

def _find_ip(device_name, input_definitions):
    """ Returns a dictionary with all network names and ips of a device. """

    networks = dict()
    
    for host_mapping in input_definitions["net_mappings"]:
        if host_mapping["host"] == device_name:
            networks[host_mapping["network"]] = host_mapping["ip"]

    for router_mapping in input_definitions["router_mappings"]:
        if router_mapping["router"] == device_name:
            networks[router_mapping["network"]] = router_mapping["ip"]

    return networks


def _find_default_route(device_name, input_definitions, flags):
    """ Returns the ip to which the device should be routed defaultly and
    None if the change of default routing is not required.
    """

    return None


def _generate_config_vars(input_definitions, flags): # TODO check what vars needs to be in config
    """ Generates vars file for all devices. """     # TODO dump to yaml without jinja

    hosts = []
    for host in input_definitions["hosts"]:
        new_host = dict()
        new_host["name"] = host["name"]
        new_host["networks"] = _find_ip(host["name"], input_definitions)
        new_host["route_to"] = _find_default_route(host["name"], input_definitions, flags)
        hosts.append(new_host)

    routers = []
    for router in input_definitions["routers"]:
        new_router = dict()
        new_router["name"] = router["name"]
        new_router["networks"] = _find_ip(router["name"], input_definitions)
        new_router["route_to"] = _find_default_route(router["name"], input_definitions, flags)
        routers.append(new_router)
    
    generate_file("config", "base_provisioning/config.yml", hosts=hosts, routers=routers)


def generate_ansible_vars(input_definitions, flags):
    """ Generates files with variables for ansible. """

    _generate_config_vars(input_definitions, flags)
    _generate_hosts_vars(input_definitions, flags)
    _generate_routers_vars(input_definitions, flags)
    _generate_device_vars(input_definitions, flags)
