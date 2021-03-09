from cyber_sandbox_creator.input_parser.sandbox import Sandbox, Device, Protocol, NetworkType
from cyber_sandbox_creator.io.writer import Writer
from typing import List, Optional, Union
from pathlib import Path


class String:
    """Ruby string attribute"""

    def __init__(self, variable: str, value: str):
        self.variable: str = variable
        self.value: str = value


class Integer:
    """Ruby integer attribute"""

    def __init__(self, variable: str, value: str):
        self.variable: str = variable
        self.value: str = value


class Block:
    """Ruby block"""

    def __init__(self, variable: str, name: Optional[str],
                 internal_variable: str, content: List,
                 note: Optional[str] = None):
        self.variable: str = variable
        self.name: Optional[str] = name
        self.internal_variable: str = internal_variable
        self.content: List = content
        self.note: Optional[str] = note

    def __iter__(self):
        return iter(self.content)


class Method:
    """Ruby method"""

    def __init__(self, variable: str, arguments: List[Union[Integer, String]],
                 single_line: bool = False):
        self.variable: str = variable
        self.arguments: List[Union[Integer, String]] = arguments
        self.single_line: bool = single_line


class Hash:
    """Ruby hash attribute"""

    def __init__(self, variable: str, content: List):
        self.variable: str = variable
        self.content: List = content


class Array:
    """Ruby array"""

    def __init__(self, variable: str, content: List):
        self.variable: str = variable
        self.content: List = content


class Vagrantfile:
    """Object with all data for Vagrantfile generation"""

    def __init__(self, sandbox: Sandbox):
        self.root: Block = Vagrantfile._create_root(sandbox)

    @staticmethod
    def _create_root(sandbox: Sandbox) -> Block:
        """Create root of the vagrantfile with all its content"""
        content: List = Vagrantfile._add_devices(sandbox)
        content.extend(Vagrantfile._add_preconfig(sandbox))
        content.extend(Vagrantfile._add_provisioning(sandbox))
        return Block("configure(\"2\")", None, "config", content)

    @staticmethod
    def _add_preconfig(sandbox: Sandbox) -> List[Block]:
        """Add pre-configuration block to Vagrantfile definition"""
        provisioner = "ansible" if sandbox.ansible_installed else "ansible_local"
        content: List = Vagrantfile._add_preconfig_attributes(sandbox)
        return [Block("vm.provision", provisioner, "ansible", content,
                      "Ansible pre-configuration")]

    @staticmethod
    def _add_preconfig_attributes(sandbox: Sandbox) -> List:
        """Add attributes to pre-configuration"""
        attributes: List = []
        attributes.append(String("playbook",
                                 sandbox.config["preconfig_playbook"]))
        attributes.append(String("inventory_path",
                                 sandbox.config["preconfig_inventory"]))
        return attributes

    @staticmethod
    def _add_provisioning(sandbox: Sandbox) -> List[Block]:
        """Add provisioning block to Vagrantfile definition"""
        provisioner = "ansible" if sandbox.ansible_installed else "ansible_local"
        content: List = Vagrantfile._add_provisioning_attributes(sandbox)
        return [Block("vm.provision", provisioner, "ansible", content,
                      "User Ansible provisioning")]

    @staticmethod
    def _add_provisioning_attributes(sandbox: Sandbox) -> List:
        """Add attributes to provisioning"""
        attributes: List = []
        attributes.append(String("playbook",
                                 sandbox.config["provisioning_playbook"]))
        return attributes

    @staticmethod
    def _add_devices(sandbox: Sandbox) -> List[Block]:
        """Add device blocks and their content to vagrantfile definition"""

        devices: List = []
        for device in sandbox.devices:
            device_attributes: List = Vagrantfile._add_device_attributes(device,
                                                                         sandbox)
            devices.append(Block("vm.define", device.name, "device",
                                 device_attributes,
                                 f"Device({device.device_type}): {device.name}"))

        return devices

    @staticmethod
    def _add_device_attributes(device: Device, sandbox: Sandbox):
        """Add attributes to devices"""

        attributes: List = []
        attributes.append(String("vm.hostname", device.name))
        attributes.append(String("vm.box", device.box))

        if device.protocol == Protocol.WINRM:
            attributes.append(String("vm.communicator", "winrm"))
            attributes.append(String("ssh.username", "windows"))
            attributes.append(String("winrm.username", "windows"))
            attributes.append(String("winrm.password", "vagrant"))

        vm_attributes: List = []
        vm_attributes.append(Integer("memory", device.memory))
        vm_attributes.append(Integer("cpus", device.cpus))
        attributes.append(Block("vm.provider", "virtualbox", "vb",
                                vm_attributes))

        for interface in device.interfaces:
            net_attributes: List = []
            net_attributes.append(String("", interface.network.type))
            net_attributes.append(String("virtualbox__intnet",
                                         interface.network.name))
            net_attributes.append(String("ip", interface.ip))
            net_attributes.append(String("netmask",
                                         interface.network.cidr.netmask))
            attributes.append(Method("vm.network", net_attributes, False))
        # TODO add attributes

        return attributes

    def generate(self, output_file: Path, template_name: str):
        """Generate Vagrantfile"""

        Writer.generate_file_from_template(output_file, template_name,
                                           self.root)
