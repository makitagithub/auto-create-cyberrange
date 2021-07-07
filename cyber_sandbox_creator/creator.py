import os
from pathlib import Path
from typing import Union, Optional

from cyber_sandbox_creator.input_parser.sandbox import Sandbox
from cyber_sandbox_creator.vagrant_generator.vagrantfile import Vagrantfile
from cyber_sandbox_creator.ansible_generator.preconfig import Preconfig
from cyber_sandbox_creator.ansible_generator.provisioning import Provision

CSC_PATH: Path = Path(__file__).parent.resolve()
CONFIGURATION_PATH: Path = CSC_PATH / "conf/configuration.yml"
FLAVORS_PATH: Path = CSC_PATH / "conf/flavors.yml"


def _process_topology_path(topology: Union[str, Path]) -> Path:
    """Validate and resolve topology path"""
    print(Path("test").resolve())
    try:
        if isinstance(topology, str):
            topology_path: Path = Path(topology).resolve()
        elif isinstance(topology, Path):
            topology_path: Path = topology.resolve()
        else:
            raise TypeError("Topology definition file path has invalid type "
                            f"\"{type(topology)}\"")
        if not topology_path.is_file():
            raise IOError(f"File \"{topology_path}\" does not exist")
    except OSError:
        raise ValueError(f"Invalid path to topology file \"{topology}\"")

    return topology_path


def _process_output_path(output_dir: Optional[Union[str, Path]],
                         topology_path: Path) -> Path:
    """Validate and resolve output directory path"""
    try:
        if output_dir is None or not output_dir:
            sandbox_path: Path = topology_path.parent / "sandbox"
        elif isinstance(output_dir, str):
            sandbox_path: Path = Path(output_dir).resolve()
        elif isinstance(output_dir, Path):
            sandbox_path: Path = output_dir.resolve()
        else:
            raise TypeError("Output directory path has invalid type "
                            f"\"{type(output_dir)}\"")
    except OSError:
        raise ValueError(f"Invalid output directory \"{output_dir}\"")

    return sandbox_path


def _process_provisioning_path(provisioning_dir: Optional[Union[str, Path]],
                               output_path: Path) -> Optional[Path]:
    """Validate and resolve user provisioning directory path"""
    try:
        if provisioning_dir is None or not provisioning_dir:
            provisioning_path = None
        elif isinstance(provisioning_dir, str):
            provisioning_path: Path = Path(provisioning_dir).resolve()
        elif isinstance(provisioning_dir, Path):
            provisioning_path: Path = provisioning_dir.resolve()
        else:
            raise TypeError("Provisioning directory path has invalid type "
                            f"\"{type(output_path)}\"")
        if provisioning_path is not None:
            if not provisioning_path.is_dir():
                raise IOError(f"Directory \"{provisioning_path}\" does not "
                              "exist")
            playbook_path: Path = provisioning_path / "playbook.yml"
            if not playbook_path.is_file():
                raise IOError("Provisioning directory should contain "
                              "\"playbook.yml\"")
    except OSError:
        raise ValueError("Invalid path to provisioning directory "
                         f"\"{provisioning_dir}\"")

    return provisioning_path


def _process_extra_vars_path(extra_vars: Optional[Union[str, Path]],
                             output_path: Path) -> Optional[Path]:
    """Validate and resolve path to Ansible extra vars file"""
    try:
        if extra_vars is None or not extra_vars:
            extra_vars_path = None
        elif isinstance(extra_vars, str):
            extra_vars_path: Path = Path(extra_vars).resolve()
        elif isinstance(extra_vars, Path):
            extra_vars_path: Path = extra_vars.resolve()
        else:
            raise TypeError("Extra vars file path has invalid type "
                            f"\"{type(output_path)}\"")
        if extra_vars_path is not None and not extra_vars_path.is_file():
            raise IOError(f"File \"{extra_vars_path}\" does not exist")
    except OSError:
        raise ValueError("Invalid path to extra variables file "
                         f"\"{extra_vars}\"")

    return extra_vars_path


def _generate_vagrantfile(sandbox_definition: Sandbox) -> None:
    """Initiate Vagrantfile generation"""
    try:
        vagrant_definition: Vagrantfile = Vagrantfile(sandbox_definition)
        vagrant_definition.generate(sandbox_definition.sandbox_dir /
                                    "Vagrantfile", "vagrantfile.j2")
    except IOError as e:
        raise RuntimeError(f"Vagrantfile could not be generated:\n{e}")


def _generate_preconfig(sandbox_definition: Sandbox) -> None:
    """Initiate preconfig directory generation"""
    try:
        Preconfig.generate_preconfig(sandbox_definition)
    except IOError as e:
        raise RuntimeError(f"Provisioning files could not be generated:\n{e}")


def _generate_provisioning(sandbox_definition: Sandbox) -> None:
    """Initiate provisioning directory generation"""
    try:
        Provision.generate_user_provisioning(sandbox_definition)
    except IOError as e:
        raise RuntimeError("User provisioning files could not be generated:"
                           f"\n{e}")


def create(topology: Union[str, Path],
           output_dir: Optional[Union[str, Path]] = None,
           ansible_installed: bool = False, border_router: bool = False,
           provisioning_dir: Optional[Union[str, Path]] = None,
           extra_vars: Optional[Union[str, Path]] = None,
           generate_provisioning: bool = False,
           verbose_ansible: bool = False) -> None:
    """Generates intermediate definition from a topology definition.

    :param topology: path to the topology definition file
    :param output_dir: path to an output directory
    :param ansible_installed: whether the host machine have ansible installed
    :param border_router: whether border router should be created
    :param provisioning_dir: path to directory with user provisioning files
    :param extra_vars: path to YAML file with additional values for Ansible
    :param generate_provisioning: whether provisioning should be regenerated
    :param verbose_ansible: whether Ansible output should be set to verbose
    """

    topology_path: Path = _process_topology_path(topology)
    output_path: Path = _process_output_path(output_dir, topology_path)
    provisioning_path: Path = _process_provisioning_path(provisioning_dir,
                                                         output_path)
    extra_vars_path: Path = _process_extra_vars_path(extra_vars, output_path)

    try:
        sandbox_definition: Sandbox = Sandbox(topology_path, CONFIGURATION_PATH,
                                              FLAVORS_PATH, output_path,
                                              border_router, ansible_installed,
                                              provisioning_path,
                                              extra_vars_path,
                                              generate_provisioning,
                                              verbose_ansible)
    except (IOError, ValueError) as e:
        raise RuntimeError(f"Definition parsing has failed:\n{e}")

    _generate_vagrantfile(sandbox_definition)
    _generate_preconfig(sandbox_definition)
    _generate_provisioning(sandbox_definition)
