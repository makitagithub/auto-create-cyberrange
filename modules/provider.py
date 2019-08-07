def _print_flavor(host, flavors, provider_attributes, devices):
    if ('memory' not in host):
        devices[host['name']].append('  vb.'
                + provider_attributes['memory'] + ' = '
                + str(flavors[host['flavor']]['memory']))
    if ('cpus' not in host):
        devices[host['name']].append('  vb.'
                + provider_attributes['cpus'] + ' = '
                + str(flavors[host['flavor']]['cores']))

def _add_params(host, flavors, provider_attributes, devices):
    if ('memory' in host):
        devices[host['name']].append('  vb.'
                + provider_attributes['memory'] + ' = '
                + str(host['memory']))
    if ('cpus' in host):
        devices[host['name']].append('  vb.'
                + provider_attributes['cpus'] + ' = '
                + str(host['cpus']))
    if ('flavor' in host and host['flavor'] in flavors):
        _print_flavor(host, flavors, provider_attributes, devices)

def _need_provider(host, provider_attributes):
    for attribute in provider_attributes:
        if (attribute in host):
            return True
    return False

def print_prov_attributes(host, flavors, provider_attributes, devices):
    if (_need_provider(host, provider_attributes)):
        devices[host['name']].append(
                "device.vm.provider \"virtualbox\" do |vb|")
        _add_params(host, flavors, provider_attributes, devices)     
        devices[host['name']].append("end")
    
