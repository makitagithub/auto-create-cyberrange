"""Contains generation of vars for routing of different types of devices."""

from conf.border_router import BORDER_ROUTER_NAME, BORDER_ROUTER_NETWORK_NAME,\
                               BORDER_ROUTER_IP


def _find_router_in_network(network_name, input_definitions):
    """Find a router in a network and return its ip."""
    for router_mapping in input_definitions["router_mappings"]:
        if router_mapping["network"] == network_name:
            return router_mapping["ip"]
    return None


def _find_networks_of_device(device_name, input_definitions):
    """Return the names of all networks a device is in."""
    networks = []

    for mapping in input_definitions["router_mappings"]:
        if mapping["router"] == device_name:
            networks.append(mapping["network"])
    if networks:
        return networks

    for mapping in input_definitions["net_mappings"]:
        if mapping["host"] == device_name:
            networks.append(mapping["network"])

    return networks


def _find_iface_ip_in_network(device_name, network, input_definitions):
    """Return the ip of the device interface inside a network."""
    for router_mapping in input_definitions["router_mappings"]:
        if router_mapping["router"] == device_name and \
           router_mapping["network"] == network:
            return router_mapping["ip"]

    for net_mapping in input_definitions["net_mappings"]:
        if net_mapping["host"] == device_name and \
           net_mapping["network"] == network:
            return net_mapping["ip"]

    print("Error: Could not find an interface for the device \"" +
          device_name + "\" in the network \"" + network + "\".")
    raise AttributeError


def _create_host_routing(target_host_name, input_definitions, flags):
    """Generate routings for the given host."""
    routings = []

    for host_mapping in input_definitions["net_mappings"]:
        if host_mapping["host"] == target_host_name:
            mapping = host_mapping
            break

    if flags["border_router"]:
        routing_to_router = dict()
        routing_to_router["default"] = True
        routing_to_router["interface_ip"] = mapping["ip"]
        gateway = _find_router_in_network(mapping["network"],
                                          input_definitions)
        routing_to_router["gateway"] = gateway
        routings.append(routing_to_router)
    else:
        for network in input_definitions["networks"]:
            if network["name"] == mapping["network"]:
                continue
            routing_to_other_hosts = dict()
            routing_to_other_hosts["default"] = False
            routing_to_other_hosts["interface_ip"] = mapping["ip"]
            gateway = _find_router_in_network(mapping["network"],
                                              input_definitions)
            routing_to_other_hosts["gateway"] = gateway
            net_ip, mask = network["cidr"].split('/')
            routing_to_other_hosts["network"] = net_ip
            routing_to_other_hosts["netmask"] = mask
            routings.append(routing_to_other_hosts)

    return routings


def _create_router_routing(router_name, input_definitions, flags):
    """Generate routings for the given router."""
    routings = []

    if flags["border_router"]:
        routing_to_br = dict()
        routing_to_br["default"] = True
        interface_ip = _find_iface_ip_in_network(router_name,
                                                 BORDER_ROUTER_NETWORK_NAME,
                                                 input_definitions)
        routing_to_br["interface_ip"] = interface_ip
        routing_to_br["gateway"] = BORDER_ROUTER_IP
        routings.append(routing_to_br)
    else:
        for network in input_definitions["networks"]:
            if network["name"] in _find_networks_of_device(router_name,
                                                           input_definitions):
                continue
            routing_to_other_router = dict()
            routing_to_other_router["default"] = False
            interface_ip = _find_iface_ip_in_network(router_name,
                                                     network["name"],
                                                     input_definitions)
            routing_to_br["interface_ip"] = interface_ip
            gateway = _find_router_in_network(network["name"],
                                              input_definitions)
            routing_to_other_router["gateway"] = gateway
            net_ip, mask = network["cidr"].split('/')
            routing_to_other_router["network"] = net_ip
            routing_to_other_router["netmask"] = mask
            routings.append(routing_to_other_router)

    return routings


def _create_border_router_routing(input_definitions, flags):
    """Generate routings for the border router."""
    routings = []

    for network in input_definitions["networks"]:
        if network["name"] == BORDER_ROUTER_NETWORK_NAME:
            continue
        routing_to_hosts = dict()
        routing_to_hosts["default"] = False
        routing_to_hosts["interface_ip"] = BORDER_ROUTER_IP
        net_ip, mask = network["cidr"].split('/')
        routing_to_hosts["network"] = net_ip
        routing_to_hosts["netmask"] = mask
        gateway = _find_router_in_network(network["name"], input_definitions)
        routing_to_hosts["gateway"] = gateway
        routings.append(routing_to_hosts)

    return routings


def add_routings(device_name, device_type, input_definitions, flags):
    """Generate routings for the given device.

    Returns a list of dicts with the syntax:
    - default: True/False
      gateway: ip of the target device
      interface_ip: ip of the device on the given interface
      network: ip of the network (if default is False)
      netmask: mask of the network (if default is False)
    """
    if not input_definitions["routers"]:
        return []

    if device_type == "host":
        return _create_host_routing(device_name, input_definitions, flags)
    elif device_type == "router":
        if device_name != BORDER_ROUTER_NAME:
            return _create_router_routing(device_name, input_definitions,
                                          flags)
        return _create_border_router_routing(input_definitions, flags)
    return []
