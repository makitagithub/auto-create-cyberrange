from modules.file_manager import generate_file

def _create_inventory(input_definitions):
    """ Creates an inventory file with host groups. """

    host_names = []
    for host in input_definitions["hosts"]:
        host_names.append(host["name"])

    router_names = []
    for router in input_definitions["routers"]:
        router_names.append(router["name"])

    generate_file("inventory", "provisioning/inventory.ini", hosts=host_names, routers=router_names)


def _create_config(input_definitions, flags):
    """ Creates a file with common variables for all roles. """

    hosts = []
    for host in input_definitions["hosts"]:
        new_host = dict()
        new_host["name"] = host["name"]
        hosts.append(new_host)

    routers = []
    for router in input_definitions["routers"]:
        new_router = dict()
        new_router["name"] = router["name"]
        routers.append(new_router)
    
    generate_file("config", "base_provisioning/config.yml", hosts=hosts, routers=routers)
    
def _create_config_playbooks(input_definitions, flags):
    """ Generates playbooks and roles for basic device configuration. """
    # TODO create playbooks
    return


def _create_user_playbooks(input_definitions):
    """ Generates template playbooks and roles for users. """

    generate_file("playbook", "provisioning/playbook.yml")
    generate_file("user_hosts", "provisioning/roles/hosts/tasks/main.yml")
    generate_file("user_routers", "provisioning/roles/routers/tasks/main.yml")

    for host in input_definitions["hosts"]:
        generate_file("user_separate_hosts", "provisioning/roles/" + host["name"] + "/tasks/main.yml", host_name=host["name"])

    for router in input_definitions["routers"]:
        generate_file("user_separate_routers", "provisioning/roles/" + router["name"] + "/tasks/main.yml", router_name=router["name"])



def generate_playbooks(input_definitions, flags):
    """ Generates ansible playbooks.

    :param definitions: device definitions structure
    :param flags: command line input flags
    """

    _create_inventory(input_definitions)
    _create_config(input_definitions, flags)
    _create_config_playbooks(input_definitions, flags)
    _create_user_playbooks(input_definitions)
