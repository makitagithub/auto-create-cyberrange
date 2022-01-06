from typing import Optional, List, Dict

from sandboxcreator.input_parser.sandbox import Network, Sandbox,\
    Interface, DevicePurpose, Device, DeviceType


class Routes:
    """Static methods for routing table changes"""

    @staticmethod
    def _find_router_interface(network: Network, sandbox: Sandbox) -> Interface:
        """Find the interface of a router inside a network"""
        for device in sandbox.devices:
            if device.device_purpose is DevicePurpose.ROUTER:
                for interface in device.interfaces:
                    if network == interface.network:
                        return interface
        raise AttributeError(f"There is no router in the network{network.name}")

    @staticmethod
    def _find_router_in_network(network: Network, sandbox: Sandbox) -> Device:
        """Find the a router inside a network"""
        for device in sandbox.devices:
            if device.device_purpose is DevicePurpose.ROUTER:
                for interface in device.interfaces:
                    if network == interface.network:
                        return device
        raise AttributeError(f"There is no router in the network{network.name}")

    @staticmethod
    def _find_br(sandbox: Sandbox) -> Optional[Device]:
        """Find border router"""
        for device in sandbox.devices:
            if device.device_purpose is DevicePurpose.BORDER_ROUTER:
                return device
        return None

    @staticmethod
    def _find_br_network(sandbox: Sandbox) -> Network:
        """Find the border router network"""
        for network in sandbox.networks:
            if network.name == sandbox.config["border_router_network_name"]:
                return network

    @staticmethod
    def _create_host_routes(device: Device, sandbox: Sandbox) -> List[Dict]:
        """Create routes for hosts (and controller)"""
        routes: List = []
        configure_auto = {
            "interface_ip": "{{ ansible_default_ipv4.address  | "
                            "default(ansible_all_ipv4_addresses[0]) }}",
            "interface_netmask": "{{ ansible_default_ipv4.netmask"
                                 "  | default('24') }}",
            "interface_default_gateway": ""}
        routes.append(configure_auto)
        if sandbox.router_present:
            router_int: Interface = Routes. \
                _find_router_interface(device.interfaces[0].network, sandbox)
            to_router = {
                "interface_ip": str(device.interfaces[0].ip),
                "interface_netmask":
                    str(device.interfaces[0].network.cidr.netmask),
                "interface_default_gateway": str(router_int.ip),
                "interface_routes": []}
            routes.append(to_router)
        return routes

    @staticmethod
    def _create_router_routes(device: Device, sandbox: Sandbox) -> List[Dict]:
        """Create routes for routers"""
        routes: List = []
        auto_route: str = "{{ ansible_default_ipv4.gateway }}"
        configure_auto = {
            "interface_ip": "{{ ansible_default_ipv4.address  | "
                            "default(ansible_all_ipv4_addresses[0]) }}",
            "interface_netmask": "{{ ansible_default_ipv4.netmask"
                                 "  | default('24') }}",
            "interface_default_gateway": auto_route}
        routes.append(configure_auto)
        return routes

    @staticmethod
    def _create_br_routes(device: Device, sandbox: Sandbox) -> List[Dict]:
        """Create routers the for border router"""
        routes: List = []
        br_network: Network = Routes._find_br_network(sandbox)
        for interface in device.interfaces:
            if interface.network is br_network:
                def_interface: Interface = interface
        to_other_networks: List = []
        for network in sandbox.networks:
            if network is br_network:
                continue
            router: Device = Routes._find_router_in_network(network, sandbox)
            for interface in router.interfaces:
                if interface.network == br_network:
                    interface_to_hosts = interface
            to_other_networks.append({"gateway": str(interface_to_hosts.ip),
                                      "network": str(network.cidr.ip),
                                      "netmask": str(network.cidr.netmask)})
        to_hosts = {
            "interface_default_gateway": "",
            "interface_ip": str(def_interface.ip),
            "interface_netmask": str(br_network.cidr.netmask),
            "interface_routes": to_other_networks}
        routes.append(to_hosts)
        return routes

    @staticmethod
    def create_routes(device: Device, sandbox: Sandbox) -> List[Dict]:
        """Create specific routes for each type of device"""
        routes: List[Dict] = []
        auto_route: str = "{{ ansible_default_ipv4.gateway }}"
        configure_auto = {
            "interface_ip": "{{ ansible_default_ipv4.address  | "
                            "default(ansible_all_ipv4_addresses[0]) }}",
            "interface_netmask": "{{ ansible_default_ipv4.netmask"
                                 "  | default('24') }}",
            "interface_default_gateway": auto_route}
        routes.append(configure_auto)

        if device.device_type is DeviceType.HOST:
            routes.extend(Routes._create_host_routes(device, sandbox))
        elif device.device_purpose is DevicePurpose.ROUTER:
            routes.extend(Routes._create_router_routes(device, sandbox))

        return routes
