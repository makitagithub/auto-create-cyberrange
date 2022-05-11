from typing import List, Dict

import psutil


def _get_available_memory() -> int:
    """Get the amount of free memory in MB on the host system"""
    available_memory = psutil.virtual_memory().available // 1024 // 1024
    return available_memory


def _get_required_memory(vm_attributes: List[Dict]) -> int:
    """Get the minimal required memory in MB for the given sandbox"""
    required_memory: int = 0
    for vm in vm_attributes:
        required_memory += vm.get("memory")
    return required_memory


def verify_available_memory(vm_attributes: List[Dict]) -> None:
    """Verify if enough memory is available to build the sandbox"""
    required_memory: int = _get_required_memory(vm_attributes)
    available_memory: int = _get_available_memory()
    if required_memory > available_memory:
        print(f"Warning: The sandbox requires {required_memory} MB of memory, "
              f"but only {available_memory} MB is available on your system.")
