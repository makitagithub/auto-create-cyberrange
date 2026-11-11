"""Translate CSC topology data into Ubuntu Netplan interface settings."""
from netaddr import IPNetwork

from sandboxcreator.input_parser.sandbox import DeviceType
from sandboxcreator.ansible_generator.routes import Routes


class Netplan:
    @staticmethod
    def create_host_vars(device, sandbox):
        interfaces = []
        for interface in device.interfaces:
            routes = []
            if device.device_type is DeviceType.HOST and sandbox.router_present:
                if interface is device.interfaces[0]:
                    gateway = Routes._find_router_interface(interface.network, sandbox)
                    routes.append({"to": "default", "via": str(gateway.ip)})
            elif device.device_type is DeviceType.ROUTER:
                for entry in Routes._create_router_routes(device, sandbox):
                    if entry["interface_ip"] == str(interface.ip):
                        for route in entry["interface_routes"]:
                            network = IPNetwork(route["network"] + "/" + route["netmask"])
                            routes.append({"to": str(network.cidr), "via": route["gateway"]})
            interfaces.append({
                "ip": str(interface.ip),
                "address": str(interface.ip) + "/" + str(interface.network.cidr.prefixlen),
                "routes": routes,
            })
        return {
            "csc_netplan_interfaces": interfaces,
            "csc_netplan_use_management_routes": not (
                device.device_type is DeviceType.HOST and sandbox.router_present),
        }
