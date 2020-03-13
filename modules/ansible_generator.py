from modules.file_manager import load_template, generate_file

def _create_inventory(input_definitions):
    """ Creates an inventory file with host groups. """

    host_names = []
    for host in input_definitions["hosts"]:
        host_names.append(host["name"])

    router_names = []
    for router in input_definitions["routers"]:
        router_names.append(router["name"])

    inventory_template = load_template("inventory")
    output = inventory_template.render(hosts=host_names, routers=router_names)
    generate_file("provisioning/inventory.ini", output)


def generate_playbooks(input_definitions, flags):
    """ Generates ansible playbooks.

    :param definitions: device definitions structure
    :param flags: command line input flags
    """

    _create_inventory(input_definitions)
