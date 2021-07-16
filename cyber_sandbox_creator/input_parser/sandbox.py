from enum import Enum
from pathlib import Path
from netaddr import IPNetwork, IPAddress

import kypo.topology_definition.models as kypo

from cyber_sandbox_creator.input_parser.topology_parser import Topology
from typing import List, Dict, Optional, Tuple
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


class NetworkType(Enum):
    """Type of network"""
    PRIVATE = 1
    PUBLIC = 2

    def __str__(self):
        return f"{self.name.lower()}_network"


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


class Network:
    """Virtual network"""

    def __init__(self, name: str, network_type: NetworkType, cidr: str):
        self.name: str = name
        self.type: NetworkType = network_type
        self.cidr: IPNetwork = IPNetwork(cidr)

    def __str__(self):
        return f"Network(name: {self.name}, type: {self.type}," \
               f" cidr: {self.cidr})"


class Interface:
    """Network interface of a device"""

    def __init__(self, network: Network, ip: str):
        self.network: Network = network
        self.ip: IPAddress = IPAddress(ip)

    def __str__(self):
        return f"Interface(network: {self.network.name}, " \
               f"type: {self.network.type}, ip: {self.ip})"


class Device:
    """A device of the sandbox"""

    def __init__(self, name: str, device_purpose: DevicePurpose, box: str,
                 memory: int, cpus: int, protocol: Protocol = Protocol.SSH,
                 interfaces: List[Interface] = []):
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
        self.protocol: Protocol = protocol
        self.memory: int = memory
        self.cpus: int = cpus
        self.interfaces: List[Interface] = interfaces

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
                 extra_vars_file: Optional[Path], generate_provisioning: bool,
                 verbose_ansible: bool):
        topology: Topology = Topology.from_file(topology_path)
        self.border_router_present: bool = border_router
        self.generate_provisioning: bool = generate_provisioning
        self.sandbox_dir: Path = sandbox_dir
        self.ansible_installed: bool = ansible_installed
        self.verbose_ansible: bool = verbose_ansible
        self.user_provisioning_dir: Optional[Path] = user_provisioning_dir
        if self.user_provisioning_dir is not None:
            self.include_requirements: bool = (self.user_provisioning_dir /
                                               "requirements.yml").is_file()
        else:
            self.include_requirements: bool = False
        self.extra_vars: Optional[Path] = extra_vars_file
        self.config: Dict = Reader.open_yaml(configuration_path)
        self.flavors: List[Flavor] = self._load_flavors(flavors_path)
        self.networks: List[Network] = self._create_network_list(topology,
                                                                 border_router,
                                                                 self.config)
        self.devices: List[Device] = self._create_device_list(topology,
                                                              self.flavors,
                                                              self.config,
                                                              border_router,
                                                              ansible_installed,
                                                              self.networks)
        self.controller_present: bool =\
            Sandbox._controller_needed(self.devices, ansible_installed)

    @classmethod
    def _create_network_list(cls, topology: Topology, border_router: bool,
                             config: Dict) -> List[Network]:
        """Create list of networks"""
        networks: List[Network] = []
        for network in topology.networks:
            networks.append(Network(network.name, NetworkType.PRIVATE,
                                    network.cidr))
        if border_router:
            networks.append(Network(config["border_router_network_name"],
                                    NetworkType.PRIVATE,
                                    config["border_router_network_ip"]))

        return networks

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
    def _controller_needed(devices: List[Device], ansible_installed: bool) \
            -> bool:
        if ansible_installed:
            return False
        for device in devices:
            if device.protocol == Protocol.WINRM:
                return True
        return False

    @staticmethod
    def _resolve_flavor(flavor_name: str, flavors: List[Flavor]) -> Tuple[int, int]:
        for flavor in flavors:
            if flavor.name == flavor_name:
                return flavor.memory, flavor.cpus
        raise AttributeError(f"Invalid flavor: {flavor_name}")

    @staticmethod
    def _create_host_device(host: kypo.Host, topology: Topology,
                            flavors: List[Flavor], config: Dict,
                            networks: List[Network]) -> Device:

        if host.flavor:
            memory, cpus = Sandbox._resolve_flavor(host.flavor, flavors)
        # TODO add explicit memory and cpus definition
        else:
            memory, cpus = 512, 2

        device_networks: List[Interface] = []
        for net_mapping in topology.net_mappings:
            if net_mapping.host == host.name:
                network = Sandbox._find_network(net_mapping.network,
                                                networks)
                device_networks.append(Interface(network, net_mapping.ip))

        if host.base_box.mgmt_protocol == kypo.Protocol.SSH:
            protocol: Protocol = Protocol.SSH
        elif host.base_box.mgmt_protocol == kypo.Protocol.WINRM:
            protocol: Protocol = Protocol.WINRM

        return Device(host.name, DevicePurpose.HOST, host.base_box.image,
                      memory, cpus, protocol, device_networks)

    @staticmethod
    def _create_router_device(router: kypo.Router, topology: Topology,
                              flavors: List[Flavor], config: Dict,
                              networks: List[Network],
                              border_router: bool, router_n: int) -> Device:

        if router.flavor:
            memory, cpus = Sandbox._resolve_flavor(router.flavor, flavors)
        # TODO add explicit memory and cpus definition
        else:
            memory, cpus = config["default_router_memory"], \
                           config["default_router_cpus"]

        device_networks: List[Interface] = []
        for router_mapping in topology.router_mappings:
            if router_mapping.router == router.name:
                network = Sandbox._find_network(router_mapping.network,
                                                networks)
                device_networks.append(Interface(network, router_mapping.ip))
        if border_router:
            for net in networks:
                if net.name == config["border_router_network_name"]:
                    br_network: Network = net
            br_ip: IPAddress = IPAddress(config["border_router_ip"])
            device_networks.append(Interface(br_network, br_ip + router_n))

        if router.base_box.mgmt_protocol == kypo.Protocol.SSH:
            protocol: Protocol = Protocol.SSH
        elif router.base_box.mgmt_protocol == kypo.Protocol.WINRM:
            protocol: Protocol = Protocol.WINRM

        return Device(router.name, DevicePurpose.ROUTER, router.base_box.image,
                      memory, cpus, protocol, device_networks)

    @staticmethod
    def _find_network(network_name: str, networks: List[Network]) -> Optional[Network]:
        """Return a Network by its name"""
        for network in networks:
            if network.name == network_name:
                return network

    @staticmethod
    def _create_border_router(config: Dict, networks: List[Network]) -> Device:
        """Creates a border router device"""
        br_network: Interface = Interface(Sandbox._find_network(config["border_router_network_name"], networks),
                                          config["border_router_ip"])

        return Device(config["border_router_name"], DevicePurpose.BORDER_ROUTER,
                      config["border_router_box"],
                      int(config["border_router_memory"]),
                      int(config["border_router_cpus"]), Protocol.SSH,
                      [br_network])

    @staticmethod
    def _find_available_ip(network: Network, devices: List[Device])\
            -> Interface:
        """Find an available IP address in a network and return the Interface"""

        all_addresses: List[IPAddress] = list(network.cidr)
        if len(all_addresses) > 5:  # avoid low addresses
            all_addresses = all_addresses[5:]
        new_ip: str = None
        for address in all_addresses:
            conflict = False
            for device in devices:
                for interface in device.interfaces:
                    if interface.network is network and interface.ip is address:
                        conflict = True
            if not conflict:
                new_ip = str(address)
                break
        return Interface(network, new_ip)

    @staticmethod
    def _create_device_list(topology: Topology, flavors: List[Flavor],
                            config: Dict, border_router: bool,
                            ansible_installed: bool,
                            networks: List[Network]) -> List[Device]:
        """Creates list of devices with all attributes"""

        devices: List[Device] = []

        if border_router:
            devices.append(Sandbox._create_border_router(config, networks))

        for host in topology.hosts:
            devices.append(Sandbox._create_host_device(host, topology, flavors,
                                                       config, networks))
        router_n: int = 0
        for router in topology.routers:
            router_n += 1
            devices.append(Sandbox._create_router_device(router, topology,
                                                         flavors, config,
                                                         networks,
                                                         border_router, router_n))
        if Sandbox._controller_needed(devices, ansible_installed):  # needs to be at the end
            devices.append(Device(config["controller_name"],
                                  DevicePurpose.CONTROLLER,
                                  config["controller_box"],
                                  int(config["controller_memory"]),
                                  int(config["controller_cpus"]), Protocol.SSH,
                                  [Sandbox._find_available_ip(networks[0], devices)]))
        print(devices[-1].interfaces)
        return sorted(devices)  # sorted by priority based on device purpose
