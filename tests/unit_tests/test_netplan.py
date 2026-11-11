from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

import yaml
from netaddr import IPNetwork

from sandboxcreator.creator import CONFIGURATION_PATH, FLAVORS_PATH
from sandboxcreator.input_parser.sandbox import Sandbox, DeviceType
from sandboxcreator.ansible_generator.netplan import Netplan
from sandboxcreator.ansible_generator.vars import Vars
from sandboxcreator.ansible_generator.preconfig import Preconfig

ROOT = Path(__file__).resolve().parents[2]


def sandbox(name, output=None):
    return Sandbox(ROOT / "topologies" / name, CONFIGURATION_PATH, FLAVORS_PATH,
                   output or ROOT / "unused-output", False, None, None, False, False)


class NetplanTests(TestCase):
    def test_standalone_host_preserves_management_routes(self):
        s = sandbox("0-routers-1-network-1-host.yml")
        result = Netplan.create_host_vars(s.devices[0], s)
        self.assertTrue(result["csc_netplan_use_management_routes"])
        self.assertEqual(result["csc_netplan_interfaces"],
                         [{"ip": "10.10.30.5", "address": "10.10.30.5/24", "routes": []}])

    def test_prefix_comes_from_topology(self):
        s = sandbox("0-routers-1-network-1-host.yml")
        s.devices[0].interfaces[0].network.cidr = IPNetwork("10.10.30.0/26")
        result = Netplan.create_host_vars(s.devices[0], s)
        self.assertEqual(result["csc_netplan_interfaces"][0]["address"], "10.10.30.5/26")

    def test_routed_hosts_use_exercise_gateway(self):
        s = sandbox("1-router-2-networks-2-hosts.yml")
        for device in s.devices:
            result = Netplan.create_host_vars(device, s)
            if device.device_type is DeviceType.HOST:
                self.assertFalse(result["csc_netplan_use_management_routes"])
                interface = result["csc_netplan_interfaces"][0]
                gateway = str(device.interfaces[0].network.cidr.network + 1)
                self.assertEqual(interface["routes"], [{"to": "default", "via": gateway}])
            else:
                self.assertTrue(result["csc_netplan_use_management_routes"])

    def test_router_static_routes_have_cidr_destinations(self):
        s = sandbox("2-routers-2-networks-2-hosts.yml")
        for device in s.devices:
            if device.device_type is not DeviceType.ROUTER:
                continue
            result = Netplan.create_host_vars(device, s)
            routes = [r for i in result["csc_netplan_interfaces"] for r in i["routes"]]
            target = "10.10.30.0/24" if device.name == "server-router" else "10.10.20.0/24"
            self.assertEqual(len(routes), 1)
            self.assertEqual(routes[0]["to"], target)
            gateway = "100.100.100.2" if device.name == "server-router" else "100.100.100.1"
            self.assertEqual(routes[0]["via"], gateway)

    def test_existing_legacy_vars_are_retained(self):
        s = sandbox("0-routers-1-network-1-host.yml")
        variables = Vars.create_host_vars(s)["home"]
        self.assertIn("routes", variables)
        self.assertIn("device_aliases", variables)
        self.assertIn("csc_netplan_interfaces", variables)

    def test_preconfig_bundles_role_on_every_generation(self):
        with TemporaryDirectory() as temporary:
            output = Path(temporary)
            s = sandbox("0-routers-1-network-1-host.yml", output)
            def fake_clone(repository, location, name):
                (location / name).mkdir(parents=True)
            with patch("sandboxcreator.io.writer.Writer.clone_git_repository", side_effect=fake_clone):
                Preconfig.generate_preconfig(s)
                role = output / "preconfig/roles/csc_netplan/tasks/main.yml"
                original = role.read_text()
                role.write_text("temporary edit")
                Preconfig.generate_preconfig(s)
                self.assertEqual(role.read_text(), original)
            variables = yaml.safe_load((output / "preconfig/host_vars/home.yml").read_text())
            self.assertEqual(variables["csc_netplan_interfaces"][0]["address"], "10.10.30.5/24")
            playbook = yaml.safe_load((output / "preconfig/playbook.yml").read_text())
            tasks = next(p["tasks"] for p in playbook if p["hosts"] == "ssh")
            selected = next(t for t in tasks if t.get("ansible.builtin.include_role"))
            self.assertIn('ansible_distribution_version == "22.04"', selected["when"])

    def test_all_shipped_topologies_generate_netplan_data(self):
        for topology in (ROOT / "topologies").glob("*.yml"):
            with self.subTest(topology=topology.name):
                s = sandbox(topology.name)
                for device in s.devices:
                    data = Netplan.create_host_vars(device, s)
                    self.assertEqual(len(data["csc_netplan_interfaces"]), len(device.interfaces))
