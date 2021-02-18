from enum import Enum
from pathlib import Path
from cyber_sandbox_creator.input_parser.topology_parser import Topology
from typing import List, Dict, Optional
from cyber_sandbox_creator.io.reader import Reader


class Protocol(Enum):
    """VM communication protocol"""
    SSH = 1
    WINRM = 2

    def __str__(self):
        return self.name


class DeviceType(Enum):
    """Type of device"""
    ROUTER = 1
    HOST = 2

    def __str__(self):
        return self.name.lower()


class DevicePurpose(Enum):
    """Function of a device - also determines building order"""
    BORDER_ROUTER = 1
    ROUTER = 2
    HOST = 3
    CONTROLLER = 4

    def __str__(self):
        return self.name.lower()


class Flavor:
    """Representation of a flavor"""

    def __init__(self, name: str, memory: int, cpus: int):
        self.name: str = name
        self.memory: int = memory
        self.cpus: int = cpus

    def __str__(self):
        return f"Flavor(name: {self.name}, memory: {self.memory} GB," \
               f"CPUs: {self.cpus})"


class Device:
    """A device of the sandbox"""

    def __init__(self, name: str, device_purpose: DevicePurpose, box: str):
        self.name: str = name
        self.device_purpose: DevicePurpose = device_purpose
        if (device_purpose is DevicePurpose.ROUTER or
                device_purpose == DevicePurpose.BORDER_ROUTER):
            self.device_type = DeviceType.ROUTER
        elif (device_purpose is DevicePurpose.HOST or
              device_purpose == DevicePurpose.CONTROLLER):
            self.device_type = DeviceType.HOST
        else:
            raise ValueError("Invalid device purpose")
        self.box: str = box
        # TODO add other attributes

    def __lt__(self, other):
        return self.device_purpose.value < other.device_purpose.value

    def __str__(self):
        return f"Device(name: {self.name}, type: {self.device_type}, purpose: " \
               f"{self.device_purpose}, box: {self.box})"


class Sandbox:
    """Structure that holds all information about the sandbox"""

    def __init__(self, topology_path: Path, configuration_path: Path,
                 flavors_path: Path, sandbox_dir: Path, border_router: bool,
                 ansible_installed: bool, user_provisioning_dir: Optional[Path],
                 extra_vars_file: Optional[Path]):
        self.border_router_present: bool = border_router
        self.sandbox_dir: Path = sandbox_dir
        self.ansible_installed: bool = ansible_installed
        self.user_provisioning_dir: Optional[Path] = user_provisioning_dir
        self.extra_vars: Optional[Dict] = self._load_extra_vars(extra_vars_file)
        self.config: Dict = Reader.open_yaml(configuration_path)
        self.flavors: List[Flavor] = self._load_flavors(flavors_path)
        self.devices: List[Device] = self._create_device_list(topology_path,
                                                              self.flavors,
                                                              self.config,
                                                              border_router)

    @classmethod
    def _load_extra_vars(cls, extra_vars_path: Optional[Path]) -> Optional[Dict]:
        """Load extra vars for ansible from YAML file to a Dict"""

        extra_vars: Optional[Dict] = None
        if extra_vars_path:
            extra_vars = Reader.open_yaml(extra_vars_path)
            if not isinstance(extra_vars, Dict):
                raise TypeError("The content of extra_vars file is invalid")

        return extra_vars

    @classmethod
    def _load_flavors(cls, flavors_path: Path) -> List[Flavor]:
        """Load list of possible flavors from configuration file"""

        flavors: List[Flavor] = []
        flavors_file_content: Dict = Reader.open_yaml(flavors_path)

        for flavor_name, attributes in flavors_file_content.items():
            memory: int = int(attributes["memory"])
            cpus: int = int(attributes["cores"])
            flavors.append(Flavor(flavor_name, memory, cpus))

        return flavors

    @staticmethod
    def _create_device_list(topology_path: Path, flavors: List[Flavor],
                            config: Dict, border_router: bool) -> List[Device]:
        """Creates list of devices with all attributes"""

        topology: Topology = Topology.from_file(topology_path)
        devices: List[Device] = []

        if border_router:
            devices.append(Device(config["border_router_name"],
                                  DevicePurpose.BORDER_ROUTER,
                                  config["border_router_box"]))

        # TODO add controller

        # for host in topology.hosts:
        # TODO add hosts
        # for router in topology.routers:
        # TODO add routers

        return devices.sort()  # sorted by priority based on device purpose
