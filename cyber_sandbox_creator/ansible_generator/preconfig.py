
from typing import List, Dict

from cyber_sandbox_creator.ansible_generator.objects import Playbook, Play,\
    Task, Module
from cyber_sandbox_creator.io.writer import Writer
from cyber_sandbox_creator.io.reader import Reader
from cyber_sandbox_creator.input_parser.sandbox import Sandbox, DeviceType,\
    Protocol


class Preconfig:
    """Pre-configuration generator"""

    @staticmethod
    def _create_inventory(sandbox: Sandbox) -> Dict:
        groups: Dict = {"hosts": {"hosts": {}}, "routers": {"hosts": {}},
                        "ssh": {"hosts": {}}, "winrm": {"hosts": {}}}
        all_devices: Dict = {}
        for device in sandbox.devices:
            all_devices[device.name] = {}
            if device.device_type == DeviceType.HOST:
                groups["hosts"]["hosts"][device.name] = {}
            elif device.device_type == DeviceType.ROUTER:
                groups["routers"]["hosts"][device.name] = {}
            if device.protocol == Protocol.SSH:
                groups["ssh"]["hosts"][device.name] = {}
            elif device.protocol == Protocol.WINRM:
                groups["winrm"]["hosts"][device.name] = {}

        return {"all": {"hosts": all_devices, "children": groups}}

    @staticmethod
    def _create_host_vars(sandbox: Sandbox) -> Dict[str, Dict]:
        """Create variables for each host"""
        host_vars: Dict[str, Dict] = {}
        for device in sandbox.devices:
            variables: Dict = {"ansible_ssh_private_key_file":
                               f".vagrant/machines/{device.name}/virtualbox/private_key"}
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
        hosts_vars: Dict = {}
        router_vars: Dict = {}
        ssh_vars: Dict = {"ansible_python_interpreter": "python3"}
        winrm_vars: Dict = {"ansible_connection": "winrm",
                            "ansible_user": "windows",
                            "ansible_password": "vagrant",
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
    def _configure_routers(sandbox: Sandbox) -> List[Task]:
        """List of tasks for all routers"""
        return [Task("Enable IP forwarding",
                     Module("sysctl", {"name": "net.ipv4.ip_forward",
                                       "value": "1",
                                       "sysctl_set": "yes",
                                       "reload": "yes"}))]

    @staticmethod
    def _configure_hosts(sandbox: Sandbox) -> List[Task]:
        """List of tasks for all hosts"""
        return [Task("Install net-tools", Module("apt", {"name": "net-tools"}))]

    @staticmethod
    def _configure_linuxes(sandbox: Sandbox) -> List[Task]:
        """List of tasks for all Linux devices"""
        return [Task("Add aliases of all devices",
                     Module("lineinfile", {"path": "/etc/hosts", "line":
                                           "{{ item.key }} {{ item.value }}"}),
                     {"loop": "{{ all.device_aliases | dict2items }}"})]

    @staticmethod
    def _create_playbook(sandbox: Sandbox) -> Playbook:
        """Generate the main playbook"""

        return Playbook([Play("Router configuration",
                              Preconfig._configure_routers(sandbox), "routers",
                              True),
                         Play("Linux configuration",
                              Preconfig._configure_linuxes(sandbox), "ssh",
                              True),
                         Play("Linux Host configuration",
                              Preconfig._configure_hosts(sandbox), "hosts:&ssh",
                              True)])

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

        inventory: Dict = Preconfig._create_inventory(sandbox)
        Writer.generate_yaml(sandbox.sandbox_dir
                             / sandbox.config["preconfig_inventory"], inventory)

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

        playbook: Playbook = Preconfig._create_playbook(sandbox)
        Writer.generate_yaml(sandbox.sandbox_dir
                             / sandbox.config["preconfig_playbook"],
                             playbook.make_dict())
