"""Contains auxiliary functions for integration testing that allow reading information from topology definition file."""

import yaml;

def get_hosts(topology_file):
    """Read and print name values for all hosts."""
    with open(topology_file) as f:
        doc = yaml.safe_load(f)

    if 'hosts' in doc:
        for value in doc['hosts']:
            print(value['name'])

def get_routers(topology_file):
    """Read and print name values for all routers."""
    with open(topology_file) as f:
        doc = yaml.safe_load(f)

    if 'routers' in doc:
        for value in doc['routers']:
            print(value['name'])

def get_box_name(box):
    """Check if given vagrant box name exists in mapping and print it or print a default value."""
    with open("./testing/box_names_mapping.yml") as f:
        BOX_NAMES_MAPPING = yaml.safe_load(f)

    if box in BOX_NAMES_MAPPING:
        print(BOX_NAMES_MAPPING[box])
    else:
        print("tmp")

def change_boxes(topology_file, new_file, value):
    """Create a copy of given topology file with all host's base_box image values changed to given value and save it as a new file."""
    with open(topology_file) as f:
        doc = yaml.safe_load(f)

    for host in doc['hosts']:
        host['base_box']['image'] = value

    with open(new_file, 'w+') as f:
        yaml.dump(doc, f)
