from yamlize import Attribute
import kypo.topology_definition.models as kypo_topology


class Extra(kypo_topology.ExtraValues):
    memory: Attribute = Attribute(type=int, default=0)
    cpus: Attribute = Attribute(type=int, default=0)
    usb_passthrough: Attribute(type=bool, default=False)


class Host(kypo_topology.Host):
    extra = Attribute(type=Extra, default=None)


class HostList(kypo_topology.HostList):
    item_type = Host


class Topology(kypo_topology.TopologyDefinition):
    hosts = Attribute(type=HostList)
