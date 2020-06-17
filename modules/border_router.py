"""Contains functions for border router creation."""

from conf.border_router import *


def _are_br_parameters_free(definitions):
    """Check if border router parameters are not already taken."""
    for host in definitions["hosts"]:
        if host["name"] == BORDER_ROUTER_NAME:
            return False

    for router in definitions["routers"]:
        if router["name"] == BORDER_ROUTER_NAME:
            return False

    for network in definitions["networks"]:
        if network["name"] == BORDER_ROUTER_NETWORK_NAME or \
           network["cidr"] == BORDER_ROUTER_NETWORK_IP:
            return False

    for net_mapping in definitions["net_mappings"]:
        if net_mapping["ip"] == BORDER_ROUTER_IP:
            return False

    for router_mapping in definitions["router_mappings"]:
        if router_mapping["ip"] == BORDER_ROUTER_IP:
            return False

    return True


def _create_mappings_to_border_router(definitions):
    """Create router_mapping entries from routers to border router."""
    for router in definitions["routers"]:
        num = definitions["routers"].index(router) + 5
        if num > 255:
            raise IndexError("Too many routers.")

        ip_address = BORDER_ROUTER_IP[:(0-len(str(num)))]
        ip_address += str(num)

        border_router = {"router": router["name"],
                         "network": BORDER_ROUTER_NETWORK_NAME,
                         "ip": ip_address}
        definitions["router_mappings"].append(border_router)


def create_border_router(definitions):
    """Add the definition of border router to definitions.

    :param definitions: device definition structure
    """
    # TODO this should be later moved to input check
    if not _are_br_parameters_free(definitions):
        raise ValueError("A device with the same name as border router "
                         "already exists.")

    _create_mappings_to_border_router(definitions)

    definitions["routers"].insert(0, {"name": BORDER_ROUTER_NAME})

    networks = {"name": BORDER_ROUTER_NETWORK_NAME,
                "cidr": BORDER_ROUTER_NETWORK_IP}
    definitions["networks"].insert(0, networks)

    router_mappings = {"router": BORDER_ROUTER_NAME, "ip": BORDER_ROUTER_IP,
                       "network": BORDER_ROUTER_NETWORK_NAME}
    definitions["router_mappings"].insert(0, router_mappings)
