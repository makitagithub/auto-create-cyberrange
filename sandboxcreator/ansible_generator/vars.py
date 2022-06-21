from pathlib import Path
from typing import Dict

from sandboxcreator.ansible_generator.routes import Routes
from sandboxcreator.input_parser.sandbox import Sandbox, Device, DeviceType
from sandboxcreator.io.writer import Writer


class Vars:

    @staticmethod
    def _get_aliases(machine: Device, sandbox: Sandbox) -> Dict[str, str]:
        """Get aliases of all devices for the hosts file of the machine"""
        aliases: Dict[str, str] = {}

        for device in sandbox.devices:
            if device.name == machine.name:
                continue
            if len(device.interfaces) == 1:
                aliases[str(device.interfaces[0].ip)] = device.name
            else:
                found: bool = False
                for interface in device.interfaces:
                    if (machine.device_type == DeviceType.HOST and machine.interfaces[0].network == interface.network)\
                            or (machine.device_type == DeviceType.ROUTER and interface.network.name == sandbox.wan.name):
                        aliases[str(interface.ip)] = device.name
                        found = True
                        break
                if not found:
                    for interface in device.interfaces:
                        if machine.device_type == DeviceType.HOST and sandbox.wan.name == interface.network.name:
                            aliases[str(interface.ip)] = device.name
                            break

        return aliases


    @staticmethod
    def create_host_vars(sandbox: Sandbox) -> Dict[str, Dict]:
        """Create variables for each host"""
        host_vars: Dict[str, Dict] = {}
        for device in sandbox.devices:
            variables: Dict = {"device_aliases": Vars._get_aliases(device, sandbox),
                               "routes": Routes.create_routes(device, sandbox)}
            host_vars[device.name] = variables

        return host_vars

    @staticmethod
    def create_group_vars(sandbox: Sandbox) -> Dict[str, Dict]:
        """Create variables for each group"""
        all_vars: Dict = {}
        if sandbox.controller_present:
            all_vars["controller_name"] = sandbox.config["controller_name"]
        hosts_vars: Dict = {}
        router_vars: Dict = {}
        ssh_vars: Dict = {"ansible_python_interpreter": "python3"}
        winrm_vars: Dict = {"ansible_connection": "winrm",
                            "ansible_user": "windows",
                            "ansible_password": "vagrant",
                            "ansible_port": 5986,
                            "ansible_winrm_transport": "basic",
                            "ansible_winrm_server_cert_validation": "ignore"}

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
    def generate_vars(sandbox: Sandbox, host_dir: Path, group_dir: Path):
        """Generate host and group vars files"""
        host_vars: Dict[str, Dict] = Vars.create_host_vars(sandbox)
        for host, variables in host_vars.items():
            if variables:
                Writer.generate_yaml(host_dir.joinpath(f"{host}.yml"),
                                     variables)

        group_vars: Dict[str, Dict] = Vars.create_group_vars(sandbox)
        for group, variables in group_vars.items():
            if variables:
                Writer.generate_yaml(group_dir.joinpath(f"{group}.yml"),
                                     variables)

    @staticmethod
    def generate_user_group_vars(group_dir: Path):
        """Generate group vars for user provisioning files needed by windows"""
        winrm_vars: Dict = {"ansible_connection": "winrm",
                            "ansible_user": "windows",
                            "ansible_password": "vagrant",
                            "ansible_port": 5986,
                            "ansible_winrm_transport": "basic",
                            "ansible_winrm_server_cert_validation": "ignore"}
        group_vars: Dict[str, Dict] = {"winrm": winrm_vars}
        for group, variables in group_vars.items():
            if variables:
                Writer.generate_yaml(group_dir.joinpath(f"{group}.yml"),
                                     variables)
