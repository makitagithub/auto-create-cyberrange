def _find_ip(hostname, net_mappings):
    for net_mapping in net_mappings:
        if (net_mapping['host'] == hostname):
            return net_mapping['ip']

def _add_ip(hostname, net_mappings, devices):
    devices[hostname].append(
            'device.vm.network :private_network, ip: \"'
            + str(_find_ip(hostname, net_mappings)) + '\"')

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
            _add_ip(hostname, yml['net_mappings'], devices)
            if (yml['networks']):
                _add_netmask(hostname, mapping['network'], yml['networks'], devices)
                

