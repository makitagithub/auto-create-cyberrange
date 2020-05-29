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


def _find_router_ip_in_br_network(other_network, input_definitions):
    """Find a router inside of a network and returns its ip in br network."""
    router = None

    for router_mapping in input_definitions["router_mappings"]:
        if router_mapping["network"] == other_network:
            router = router_mapping["router"]

    if not router:
        return None

    for router_mapping in input_definitions["router_mappings"]:
        if router_mapping["router"] == router and\
           router_mapping["network"] == BORDER_ROUTER_NETWORK_NAME:
            return router_mapping["ip"]


def _create_host_routing(target_host_name, input_definitions, flags):
    """Generate routes for the given host."""
    simple_routes = []
    default_route = None
    mapping = None

    for host_mapping in input_definitions["net_mappings"]:
        if host_mapping["host"] == target_host_name:
            mapping = host_mapping
            break

    if not mapping:
        raise ValueError("Host was not found: " + target_host_name)

    if flags["border_router"]:
        default_route = dict()
        default_route["interface_ip"] = mapping["ip"]
        gateway = _find_router_in_network(mapping["network"],
                                          input_definitions)
        default_route["gateway"] = gateway
    else:
        for network in input_definitions["networks"]:
            if network["name"] == mapping["network"]:
                continue
            routing_to_other_hosts = dict()
            routing_to_other_hosts["interface_ip"] = mapping["ip"]
            gateway = _find_router_in_network(mapping["network"],
                                              input_definitions)
            routing_to_other_hosts["gateway"] = gateway
            net_ip, mask = network["cidr"].split('/')
            routing_to_other_hosts["network"] = net_ip
            routing_to_other_hosts["netmask"] = mask
            simple_routes.append(routing_to_other_hosts)

    return simple_routes, default_route


def _create_router_routing(router_name, input_definitions, flags):
    """Generate routes for the given router."""
    simple_routes = []
    default_route = None

    if flags["border_router"]:
        default_route = dict()
        interface_ip = _find_iface_ip_in_network(router_name,
                                                 BORDER_ROUTER_NETWORK_NAME,
                                                 input_definitions)
        default_route["interface_ip"] = interface_ip
        default_route["gateway"] = BORDER_ROUTER_IP

    return simple_routes, default_route


def _create_border_router_routing(input_definitions):
    """Generate routes for the border router."""
    simple_routes = []
    default_route = None

    for network in input_definitions["networks"]:
        if network["name"] == BORDER_ROUTER_NETWORK_NAME:
            continue
        routing_to_hosts = dict()
        routing_to_hosts["interface_ip"] = BORDER_ROUTER_IP
        net_ip, mask = network["cidr"].split('/')
        routing_to_hosts["network"] = net_ip
        routing_to_hosts["netmask"] = mask
        gateway = _find_router_ip_in_br_network(network["name"],
                                                input_definitions)
        routing_to_hosts["gateway"] = gateway
        simple_routes.append(routing_to_hosts)

    return simple_routes, default_route


def add_routings(device_name, device_type, input_definitions, flags):
    """Generate simple and default routes for the given device.

    Returns a list of dicts with the syntax:
    - gateway: ip of the target device
      interface_ip: ip of the device on the given interface
      network: ip of the network (if default is False)
      netmask: mask of the network (if default is False)
    """
    if not input_definitions["routers"]:
        return dict()

    routes = {"simple": [], "default": dict()}

    if device_type == "host":
        simple, default = _create_host_routing(device_name, input_definitions,
                                               flags)
    elif device_type == "router":
        if device_name != BORDER_ROUTER_NAME:
            simple, default = _create_router_routing(device_name,
                                                     input_definitions, flags)
        else:
            simple, default = _create_border_router_routing(input_definitions)
    else:
        raise KeyError("Unsupported device type: " + str(device_type))

    routes["simple"] = simple
    if default:
        routes["default"] = default

    return routes
