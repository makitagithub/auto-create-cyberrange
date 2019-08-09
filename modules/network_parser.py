def _find_ip(hostname, mappings, device_type):
    for mapping in mappings:
        if ((device_type == 'host'
                and mapping['host'] and mapping['host'] == hostname)
                or (device_type == 'router'
                and mapping['router'] and mapping['router'] == hostname)):
            return mapping['ip']

def _add_ip(hostname, mappings, device_type, devices):
    devices[hostname].append(
            'device.vm.network :private_network, ip: \"'
            + str(_find_ip(hostname, mappings, device_type)) + '\"')

def _add_netmask(hostname, my_network, networks, devices):
    for network in networks:
        if (network['name'] == my_network):
            address, mask = network['cidr'].split('/')
            devices[hostname][-1] += (', netmask: ' + mask)

def add_networks(hostname, yml, devices):

    if (not yml['net_mappings']):
        return

    for mapping in yml['net_mappings']:
        if (mapping['host'] == hostname):
            _add_ip(hostname, yml['net_mappings'], 'host', devices)
            if (yml['networks']):
                _add_netmask(
                        hostname, mapping['network']
                        , yml['networks'], devices)

def _add_router_os(routername, devices):
    router_os = 'generic/debian10'
    devices[routername].append('device.vm.box = \"' + router_os + '\"')

def add_routers(routername, yml, devices):

    if (not yml['router_mappings']):
        return

    for mapping in yml['router_mappings']:
        if (mapping['router'] == routername):
            _add_router_os(routername, devices)
            _add_ip(routername, yml['router_mappings'], 'router', devices)

