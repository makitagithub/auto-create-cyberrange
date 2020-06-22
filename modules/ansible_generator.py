"""Contain functions for ansible file generation."""

from modules.file_manager import generate_file, copy_template_file
from modules.ansible_vars_generator import generate_ansible_vars
from conf.border_router import BORDER_ROUTER_NAME


def _create_config_playbooks(input_definitions, flags):
    """Generate playbooks and roles for basic device configuration."""
    copy_template_file("device_configuration",
                       "base_provisioning/device_configuration.yml")
    if input_definitions["hosts"]:
        copy_template_file("hosts",
                           "base_provisioning/roles/hosts/tasks/main.yml")

    if input_definitions["routers"]:
        copy_template_file("routers",
                           "base_provisioning/roles/routers/tasks/main.yml")

    for device in input_definitions["hosts"] + input_definitions["routers"]:
        if "border_router" in flags and flags["border_router"] and\
           device["name"] == BORDER_ROUTER_NAME:
            copy_template_file("br", "base_provisioning/roles/" +
                               device["name"] + "/tasks/main.yml")
        else:
            copy_template_file("separate_devices", "base_provisioning/roles/" +
                               device["name"] + "/tasks/main.yml")


def _create_user_playbooks(input_definitions):
    """Generate template playbooks and roles for users."""
    copy_template_file("playbook", "provisioning/playbook.yml")
    if input_definitions["hosts"]:
        copy_template_file("user_hosts",
                           "provisioning/roles/hosts/tasks/main.yml")
    if input_definitions["routers"]:
        copy_template_file("user_routers",
                           "provisioning/roles/routers/tasks/main.yml")

    for host in input_definitions["hosts"]:
        generate_file("user_separate_hosts",
                      "provisioning/roles/" + host["name"] + "/tasks/main.yml",
                      host_name=host["name"])

    for router in input_definitions["routers"]:
        generate_file("user_separate_routers",
                      "provisioning/roles/" + router["name"] +
                      "/tasks/main.yml", router_name=router["name"])


def generate_playbooks(input_definitions, flags):
    """Generate ansible vars and playbooks.

    :param input_definitions: device definitions structure
    :param flags: command line input flags
    """
    generate_ansible_vars(input_definitions, flags)
    _create_config_playbooks(input_definitions, flags)
    _create_user_playbooks(input_definitions)
