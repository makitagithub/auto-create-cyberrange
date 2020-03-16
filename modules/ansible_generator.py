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
    
    config_template = load_template("config")
    output = config_template.render(hosts=hosts, routers=routers)
    generate_file("base_provisioning/config.yml", output)
    
def _create_config_playbooks(input_definitions, flags):
    """ Generates playbooks and roles for basic device configuration. """
    # TODO create playbooks
    return


def _create_user_playbooks(input_definitions):
    """ Generates template playbooks and roles for users. """

    playbook_template = load_template("playbook")
    generate_file("provisioning/playbook.yml", playbook_template.render())

    user_hosts_template = load_template("user_hosts")
    generate_file("provisioning/roles/hosts/tasks/main.yml", user_hosts_template.render())

    user_routers_template = load_template("user_routers")
    generate_file("provisioning/roles/routers/tasks/main.yml", user_routers_template.render())

    user_host_template = load_template("user_separate_hosts")
    for host in input_definitions["hosts"]:
        output = user_host_template.render(host_name=host["name"])
        generate_file("provisioning/roles/" + host["name"] + "/tasks/main.yml", output)

    user_router_template = load_template("user_separate_routers")
    for router in input_definitions["routers"]:
        output = user_router_template.render(router_name=router["name"])
        generate_file("provisioning/roles/" + router["name"] + "/tasks/main.yml", output)



def generate_playbooks(input_definitions, flags):
    """ Generates ansible playbooks.

    :param definitions: device definitions structure
    :param flags: command line input flags
    """

    _create_inventory(input_definitions)
    _create_config(input_definitions, flags)
    _create_config_playbooks(input_definitions, flags)
    _create_user_playbooks(input_definitions)
