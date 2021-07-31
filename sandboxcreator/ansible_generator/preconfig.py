from typing import Dict
from pathlib import Path

from sandboxcreator.ansible_generator.routes import Routes
from sandboxcreator.io.writer import Writer
from sandboxcreator.io.reader import Reader
from sandboxcreator.input_parser.sandbox import Sandbox


class Preconfig:
    """Pre-configuration generator"""

    @staticmethod
    def _create_host_vars(sandbox: Sandbox) -> Dict[str, Dict]:
        """Create variables for each host"""
        host_vars: Dict[str, Dict] = {}
        for device in sandbox.devices:
            variables: Dict = {"routes": Routes.create_routes(device, sandbox)}
            host_vars[device.name] = variables

        return host_vars

    @staticmethod
    def _create_group_vars(sandbox: Sandbox) -> Dict[str, Dict]:
        """Create variables for each group"""
        aliases: Dict[str, str] = {}
        for device in sandbox.devices:
            for interface in device.interfaces:
                aliases[str(interface.ip)] = device.name

        all_vars: Dict = {"device_aliases": aliases}
        if sandbox.border_router_present:
            all_vars["border_router_name"] = sandbox.config["border_router_name"]
        if sandbox.controller_present:
            all_vars["controller_name"] = sandbox.config["controller_name"]
        hosts_vars: Dict = {}
        router_vars: Dict = {}
        ssh_vars: Dict = {"ansible_python_interpreter": "python3"}
        winrm_vars: Dict = {"ansible_connection": "winrm",
                            "ansible_user": "windows",
                            "ansible_password": "vagrant",
                            "ansible_become_pass": "vagrant",
                            "ansible_winrm_transport": "basic",
                            "ansible_winrm_server_cert_validation": "ignore",
                            "ansible_winrm_scheme": "http"}

        if sandbox.ansible_installed:
            ssh_vars.update({"ansible_host": "127.0.0.1",
                             "ansible_user": "vagrant"})
        else:
            ssh_vars.update({"ansible_connection": "local"})

        group_vars: Dict[str, Dict] = {"all": all_vars, "hosts": hosts_vars,
                                       "routers": router_vars, "ssh": ssh_vars,
                                       "winrm": winrm_vars}
        return group_vars

    @staticmethod
    def _preconfig_exists(sandbox) -> bool:
        """Check whether the provisioning directory already exists"""
        return Reader.dir_exists(sandbox.sandbox_dir /
                                 sandbox.config["preconfig_dir"])

    @staticmethod
    def generate_preconfig(sandbox: Sandbox) -> None:
        """Generate all files for pre-configuration"""

        if Preconfig._preconfig_exists(sandbox):
            Writer.remove_directory(sandbox.sandbox_dir /
                                    sandbox.config["preconfig_dir"])

        Writer.clone_git_repository(sandbox.config["common_repo"],
                                    sandbox.sandbox_dir / sandbox.config["preconfig_roles"])
        Writer.clone_git_repository(sandbox.config["interface_repo"],
                                    sandbox.sandbox_dir / sandbox.config["preconfig_roles"])

        host_vars: Dict[str, Dict] = Preconfig._create_host_vars(sandbox)
        for host, variables in host_vars.items():
            if variables:
                Writer.generate_yaml(sandbox.sandbox_dir
                                     / sandbox.config["preconfig_host_vars"]
                                     / f"{host}.yml", variables)

        group_vars: Dict[str, Dict] = Preconfig._create_group_vars(sandbox)
        for group, variables in group_vars.items():
            if variables:
                Writer.generate_yaml(sandbox.sandbox_dir
                                     / sandbox.config["preconfig_group_vars"]
                                     / f"{group}.yml", variables)

        Writer.copy_file(Path(__file__).parent.parent /
                         "resources/files/playbook.yml", sandbox.sandbox_dir /
                         sandbox.config["preconfig_playbook"])
