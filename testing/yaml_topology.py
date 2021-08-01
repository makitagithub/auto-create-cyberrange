"""Contains auxiliary functions for integration testing that allow reading information from topology definition file."""

import yaml
import sys

def get_hosts(topology_file):
    """Read and print name values for all hosts."""
    stdout = open(sys.__stdout__.fileno(),
        mode=sys.__stdout__.mode,
        buffering=1,
        encoding=sys.__stdout__.encoding,
        errors=sys.__stdout__.errors,
        newline='\n',
        closefd=False)

    with open(topology_file) as f:
        doc = yaml.safe_load(f)

    if 'hosts' in doc:
        for value in doc['hosts']:
            print(value['name'], file=stdout)

def get_network_for_host(topology_file, host):
    """Read and print network value for host's net_mapping."""
    stdout = open(sys.__stdout__.fileno(),
        mode=sys.__stdout__.mode,
        buffering=1,
        encoding=sys.__stdout__.encoding,
        errors=sys.__stdout__.errors,
        newline='\n',
        closefd=False)

    with open(topology_file) as f:
        doc = yaml.safe_load(f)

    for mapping in doc['net_mappings']:
        if mapping['host'] == host:
            print(mapping['network'], file=stdout)

def get_ip_for_host(topology_file, host):
    """Read and print ip value for host's net_mapping."""
    stdout = open(sys.__stdout__.fileno(),
        mode=sys.__stdout__.mode,
        buffering=1,
        encoding=sys.__stdout__.encoding,
        errors=sys.__stdout__.errors,
        newline='\n',
        closefd=False)

    with open(topology_file) as f:
        doc = yaml.safe_load(f)

    for mapping in doc['net_mappings']:
        if mapping['host'] == host:
            print(mapping['ip'], file=stdout)

def get_router_for_network(topology_file, network):
    """Read and print router value for network's router_mapping."""
    stdout = open(sys.__stdout__.fileno(),
        mode=sys.__stdout__.mode,
        buffering=1,
        encoding=sys.__stdout__.encoding,
        errors=sys.__stdout__.errors,
        newline='\n',
        closefd=False)

    with open(topology_file) as f:
        doc = yaml.safe_load(f)

    for mapping in doc['router_mappings']:
        if mapping['network'] == network:
            print(mapping['router'], file=stdout)

def get_routers(topology_file):
    """Read and print name values for all routers."""
    stdout = open(sys.__stdout__.fileno(),
        mode=sys.__stdout__.mode,
        buffering=1,
        encoding=sys.__stdout__.encoding,
        errors=sys.__stdout__.errors,
        newline='\n',
        closefd=False)

    with open(topology_file) as f:
        doc = yaml.safe_load(f)

    if 'routers' in doc:
        for value in doc['routers']:
            print(value['name'], file=stdout)

def get_box_name(mapping_file, box):
    """Check if given vagrant box name exists in mapping and print it or print a default value."""
    stdout = open(sys.__stdout__.fileno(),
        mode=sys.__stdout__.mode,
        buffering=1,
        encoding=sys.__stdout__.encoding,
        errors=sys.__stdout__.errors,
        newline='\n',
        closefd=False)

    with open(mapping_file) as f:
        mapping = yaml.safe_load(f)

    if box in mapping:
        print(mapping[box], file=stdout)
    else:
        print("tmp", file=stdout)

def get_box_memory(mapping_file, box):
    stdout = open(sys.__stdout__.fileno(),
        mode=sys.__stdout__.mode,
        buffering=1,
        encoding=sys.__stdout__.encoding,
        errors=sys.__stdout__.errors,
        newline='\n',
        closefd=False)

    with open(mapping_file) as f:
        mapping = yaml.safe_load(f)

    if box in mapping:
        print(mapping[box], file=stdout)

def change_boxes(topology_file, new_file, value, memory):
    """Create a copy of given topology file with all host's base_box image values changed to given value and save it as a new file."""
    with open(topology_file) as f:
        doc = yaml.safe_load(f)

    for host in doc['hosts']:
        host['base_box']['image'] = value
        host['memory'] = memory

    with open(new_file, 'w+') as f:
        yaml.dump(doc, f)
