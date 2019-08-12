def _find_ip(hostname, mappings, device_type):
    """ Finds the ip address of a device. """

    for mapping in mappings:
        if ((device_type == 'host'
                and mapping['host'] and mapping['host'] == hostname)
                or (device_type == 'router'
                and mapping['router'] and mapping['router'] == hostname)):
            return mapping['ip']


def _add_ip(hostname, mappings, device_type, definitions):
    """ Adds a formatted ip address to a device definition. """

    definitions[hostname].append(
            "device.vm.network :private_network, ip: \""
            + str(_find_ip(hostname, mappings, device_type)) + '\"')


def _add_netmask(hostname, my_network, networks, definitions):
    """ Adds netmask to the end of a formatted ip definition. """

    for network in networks:
        if (network['name'] == my_network):
            address, mask = network['cidr'].split('/')
            definitions[hostname][-1] += (', netmask: ' + mask)


def add_networks(hostname, yml, definitions):
    """ Adds ip address and natmask to a host. """

    if (not yml['net_mappings']):
        return

    for mapping in yml['net_mappings']:
        if (mapping['host'] == hostname):
            _add_ip(hostname, yml['net_mappings'], 'host', definitions)
            if (yml['networks']):
                _add_netmask(
                        hostname, mapping['network']
                        , yml['networks'], definitions)


def add_router_ip(routername, yml, definitions):
    """ Adds ip address to a router. """

    if (not yml['router_mappings']):
        return

    for mapping in yml['router_mappings']:
        if (mapping['router'] == routername):
            _add_ip(routername, yml['router_mappings'], 'router', definitions)

