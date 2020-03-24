from modules.file_manager import generate_file, copy_template_file
from modules.ansible_vars_generator import generate_ansible_vars

    
def _create_config_playbooks(input_definitions, flags):
    """ Generates playbooks and roles for basic device configuration. """

    for device in input_definitions["hosts"] + input_definitions["routers"]:
        generate_file("separate_devices", "base_provisioning/roles/" + device["name"] + "/tasks/main.yml")

    # TODO create other playbooks
    return


def _create_user_playbooks(input_definitions):
    """ Generates template playbooks and roles for users. """

    copy_template_file("playbook", "provisioning/playbook.yml")
    copy_template_file("user_hosts", "provisioning/roles/hosts/tasks/main.yml")
    copy_template_file("user_routers", "provisioning/roles/routers/tasks/main.yml")

    for host in input_definitions["hosts"]:
        generate_file("user_separate_hosts", "provisioning/roles/" + host["name"] + "/tasks/main.yml", host_name=host["name"])

    for router in input_definitions["routers"]:
        generate_file("user_separate_routers", "provisioning/roles/" + router["name"] + "/tasks/main.yml", router_name=router["name"])


def generate_playbooks(input_definitions, flags):
    """ Generates ansible vars and playbooks.

    :param definitions: device definitions structure
    :param flags: command line input flags
    """
    generate_ansible_vars(input_definitions, flags)
    _create_config_playbooks(input_definitions, flags)
    _create_user_playbooks(input_definitions)
