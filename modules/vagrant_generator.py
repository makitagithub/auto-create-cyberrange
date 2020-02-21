""" This module generates a Vagrantfile from input device definitions. """


def _create_commands(device_name, device_type, input_definitions, flags):
    """ This function creates basic vagrant definition commands for a device. """

    # TODO create vagrant commands


def _build_vagrant_definitions(input_definitions, flags):
    """
    Creates a definition structure that is more suitable for Vagrantfile
    generation than input definitions.
    """

    vagrant_definitions = []

    for router in input_definitions["routers"]:
        device = dict()
        device["device_name"] = router["name"]
        device["device_type"] = "router"
        device["commands"] = _create_commands(router["name"], "router", input_definitions, flags)
        vagrant_definitions.append(device)

    for host in input_definitons["hosts"]:
        device = dict()
        device["device_name"] = host["name"]
        device["device_type"] = "host"
        device["commands"] = _create_commands(host["name"], "host", input_definitions, flags)
        vagrant_definitions.append(device)
        
    return vagrant_definitions


def generate_vagrantfile(input_definitions, flags):
    """
    This method is responsible for Vagrantfile generation.

    :param input_definitions: device definitions from the input file
    :param flags: command line flags
    """

    try:
        vagrant_definitions = _build_vagrant_definitions(input_definitions, flags)
   except Exception:
       print("Could not create definitions for Vagrantfile.")
       raise

   # TODO build Vagrantfile using a template
