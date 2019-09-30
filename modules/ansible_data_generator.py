def create_network_map(net_mappings, router_mappings):
    """ Creates a structure with network topology for Jinja2 template. """

    routings = []

    for router_mapping in router_mappings:
        routing = dict()
        routing["router_name"] = router_mapping["router"]
        routing["router_ip"] = router_mapping["ip"]
        routings.append(routing)

    return routings


def _find_router_ip(network_name, router_mappings):
    for router_mapping in router_mappings:
        if router_mapping["network"] == network_name:
            return router_mapping["ip"]


def create_host_map(net_mappings, router_mappings):
    """ Creates a structure with hosts and their primary routers ip """

    hosts = []

    for net_mapping in net_mappings:
        host = dict()
        host["host_name"] = net_mapping["host"]
        host["host_ip"] = net_mapping["ip"]
        host["router_ip"] = _find_router_ip(
            net_mapping["network"], router_mappings)
        hosts.append(host)
    return hosts
