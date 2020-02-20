import conf.border_router


def _are_br_parameters_free(definitions):
    """ Checks if border router parameters are not already taken. """

    for host in definitions["hosts"]:
        if host["name"] == BORDER_ROUTER_NAME:
            return False

    for router in definitions["routers"]:
        if router["name"] == BORDER_ROUTER_NAME:
            return False
    
    for network in definitions["networks"]:
        if network["name"] == BORDER_ROUTER_NETWORK_NAME or network["cidr"] == BORDER_ROUTER_NETWORK_IP:
            return False

    for net_mapping in definitions["net_mappings"]:
        if net_mapping["ip"] == BORDER_ROUTER_IP:
            return False


    for router_mapping in definitions["router_mappings"]:
        if router_mapping["ip"] == BORDER_ROUTER_IP:
            return False

    return True


def _create_mappings_to_border_router(definitions):
    """ Creates router_mapping entries from routers to border router. """

    for router in definitions["routers"]:
        num = definitions["routers"].index(router) + 5
        if num > 255:
            print("Error: Too many routers.")
            raise IndexError

        ip = BORDER_ROUTER_IP[:(0-len(str(num)))]
        ip += str(num)

        definitions["router_mappings"].append({"router":router["name"]
                                              ,"network":BORDER_ROUTER_NETWORK_NAME
                                              ,"ip":ip}) 
        

def create_border_router(definitions):
    """
    Adds the definition of border router to definitions.

    :param definitions: device definition structure
    """

    # TODO this should be later moved to input check
    if not _are_br_parameters_free:
        print("Error: A device with the same name as border router already exists.")
        raise ValueError

    _create_mappings_to_border_router(definitions)

    definitions["routers"].append({"name":BORDER_ROUTER_NAME })
    definitions["networks"].append({"name":BORDER_ROUTER_NETWORK_NAME
                                    ,"cidr":BORDER_ROUTER_NETWORK_IP})
    definitions["router_mappings"].append({"router":BORDER_ROUTER_NAME
                                          ,"network":BORDER_ROUTER_NETWORK_NAME
                                          ,"ip":BORDER_ROUTER_IP} )


