import re
from pathlib import Path
from typing import List, Dict

from sandboxcreator.hw_resources.memory import verify_available_memory
from sandboxcreator.hw_resources.cpu import verify_available_cpus
from sandboxcreator.hw_resources.disc import verify_available_disc_space
from sandboxcreator.io.reader import Reader


def _parse_vagrantfile(vagrantfile: str) -> List[Dict]:
    """Parse the vagrantfile for machine attributes"""
    machines = []
    for vm_definition in re.findall(r"^  config\.vm\.define.+?^  end", vagrantfile, re.MULTILINE | re.DOTALL):
        vm = {"hostname": re.search(r"\.vm\.hostname = \"(.+)\"", vm_definition).group(1),
              "box": re.search(r"\.vm\.box = \"(.+)\"", vm_definition).group(1),
              "memory": int(re.search(r"\.memory = (\d+)", vm_definition).group(1)),
              "cpus": int(re.search(r"\.cpus = (\d+)", vm_definition).group(1))}
        machines.append(vm)
    return machines


def check_hw_resources(sandbox_directory: str) -> None:
    """Check if the available hw resources can handle the given sandbox"""
    vagrantfile_path: Path = Path(sandbox_directory).joinpath("Vagrantfile")
    if not vagrantfile_path.is_file():
        return
    vagrantfile: str = Reader.get_textfile(vagrantfile_path)
    vm_attributes: List[Dict] = _parse_vagrantfile(vagrantfile)
    verify_available_memory(vm_attributes)
    verify_available_cpus(vm_attributes)
    verify_available_disc_space(vm_attributes, sandbox_directory)
