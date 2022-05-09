import re
from typing import List

import psutil


def _get_available_memory() -> int:
    """Get the amount of free memory in MB on the host system"""
    available_memory = psutil.virtual_memory().available // 1024 // 1024
    return available_memory


def _get_required_memory(vagrantfile: str) -> int:
    """Get the minimal required memory in MB for the given sandbox"""
    regex = r"\.memory = (\d+)"
    memories: List[str] = re.findall(regex, vagrantfile)
    required_memory: int = 0
    for memory in memories:
        required_memory += int(memory)
    return required_memory


def verify_available_memory(vagrantfile: str) -> None:
    """Verify if enough memory is available to build the sandbox"""
    required_memory: int = _get_required_memory(vagrantfile)
    available_memory: int = _get_available_memory()
    if required_memory > available_memory:
        print(f"Warning: The sandbox requires {required_memory} MB of memory, "
              f"but only {available_memory} MB is available on your system.")
