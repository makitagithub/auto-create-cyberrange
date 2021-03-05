from pathlib import Path
from typing import Union, Optional

from cyber_sandbox_creator.input_parser.sandbox import Sandbox
from cyber_sandbox_creator.vagrant_generator.vagrantfile import Vagrantfile
from cyber_sandbox_creator.ansible_generator.preconfig import Preconfig

CSC_PATH: Path = Path(__file__).parent.resolve()
CONFIGURATION_PATH: Path = CSC_PATH / "conf/configuration.yml"
FLAVORS_PATH: Path = CSC_PATH / "conf/flavors.yml"


def create(topology: Union[str, Path], output_dir: Union[str, Path],
           ansible_installed: bool = False, border_router: bool = False,
           provisioning_dir: Optional[Union[str, Path]] = None,
           extra_vars: Optional[Union[str, Path]] = None) -> None:
    """Generates intermediate definition from a topology definition.

    :param topology: path to the topology definition file
    :param output_dir: path to an output directory
    :param ansible_installed: whether the host machine have ansible installed
    :param border_router: whether border router should be created
    :param provisioning_dir: path to directory with user provisioning files
    :param extra_vars: path to YAML file with additional values for Ansible
    """

    try:
        if type(topology) == str:
            topology_path: Path = Path(topology).resolve()
        elif type(topology) == Path:
            topology_path: Path = topology.resolve()
        else:
            raise TypeError("Topology definition file path has invalid type"
                            f"\"{type(topology)}\"")
        if not topology_path.is_file():
            raise IOError(f"File \"{topology_path}\" does not exist")
    except OSError:
        raise ValueError(f"Invalid path to topology file \"{topology}\"")

    try:
        if type(output_dir) == str:
            sandbox_path: Path = Path(output_dir).resolve()
        elif type(output_dir) == Path:
            sandbox_path: Path = output_dir.resolve()
        else:
            raise TypeError("Output directory path has invalid type "
                            f"\"{type(output_dir)}\"")
    except OSError:
        raise ValueError(f"Invalid output directory \"{output_dir}\"")

    try:
        user_provisioning_path: Optional[Path] = None
        if provisioning_dir:
            if type(provisioning_dir) == str:
                user_provisioning_path = Path(provisioning_dir).resolve()
            elif type(provisioning_dir) == Path:
                user_provisioning_path = provisioning_dir.resolve()
            else:
                raise TypeError("Provisioning directory path has invalid type "
                                f"\"{type(output_dir)}\"")
            if not user_provisioning_path.is_dir():
                raise IOError(f"Directory \"{user_provisioning_path}\" "
                              "does not exist")
            playbook: Path = user_provisioning_path / "playbook.yml"
            if not playbook.is_file():
                raise IOError("Provisioning directory should contain "
                              "\"playbook.yml\"")
    except OSError:
        raise ValueError("Invalid path to provisioning directory "
                         f"\"{provisioning_dir}\"")

    try:
        extra_vars_path: Optional[Path] = None
        if extra_vars:
            if type(extra_vars) == str:
                extra_vars_path = Path(extra_vars).resolve()
            elif type(extra_vars) == Path:
                extra_vars_path = extra_vars.resolve()
            else:
                raise TypeError("Extra vars file path has invalid type "
                                f"\"{type(output_dir)}\"")
            if not extra_vars_path.is_file():
                raise IOError(f"File \"{extra_vars_path}\" does not exist")
    except OSError:
        raise ValueError("Invalid path to extra variables file "
                         f"\"{extra_vars}\"")

    try:
        sandbox_definition: Sandbox = Sandbox(topology_path, CONFIGURATION_PATH,
                                              FLAVORS_PATH, sandbox_path,
                                              border_router, ansible_installed,
                                              user_provisioning_path,
                                              extra_vars_path)
    except (IOError, ValueError) as e:
        raise RuntimeError(f"Definition parsing has failed:\n{e}")

    try:
        vagrant_definition: Vagrantfile = Vagrantfile(sandbox_definition)
        vagrant_definition.generate(sandbox_definition.sandbox_dir /
                                    "Vagrantfile", "vagrantfile.j2")
    except IOError as e:
        raise RuntimeError(f"Vagrantfile could not be generated:\n{e}")

    try:
        Preconfig.generate_preconfig(sandbox_definition)
    except IOError as e:
        raise RuntimeError(f"Provisioning files could not be generated:\n{e}")
