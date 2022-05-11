from typing import List, Dict

import psutil


def _get_available_cpus() -> int:
    """Get the number of CPU cores on the host system"""
    available_cpus = psutil.cpu_count()
    return available_cpus


def _get_required_cpus(vm_attributes: List[Dict]) -> int:
    """Get the minimal number of CPU cores for the given sandbox"""
    required_cpus: int = 0
    for vm in vm_attributes:
        required_cpus += vm.get("cpus")
    return required_cpus


def verify_available_cpus(vm_attributes: List[Dict]) -> None:
    """Verify if enough CPU cores are available"""
    required_cpus: int = _get_required_cpus(vm_attributes)
    available_cpus: int = _get_available_cpus()
    if required_cpus > available_cpus:
        print(f"Warning: The sandbox requires {required_cpus} CPU cores, but "
              f"only {available_cpus} CPU cores are available on your system. "
              "It may cause issues.")
