from typing import Dict, List

import psutil


def _get_available_disc_space(directory: str) -> int:
    """Get the available disc space on the host system in MB"""
    available_disk_space: int = int(psutil.disk_usage(directory).free) // 1024 // 1024
    return available_disk_space


def _estimate_box_space_requirements(box_name: str) -> int:
    """Estimate the required disc space for the box in MB"""

    # hard-coded values based on our measurements, might differ at other machines 
    generic_linux_required_space: int = 8 * 1024  # MB
    kali_linux_required_space: int = 23 * 1024  # MB
    windows_required_space: int = 30 * 1024  # MB

    if "windows" in box_name:
        return windows_required_space
    if "kali" in box_name:
        return kali_linux_required_space
    return generic_linux_required_space


def _get_required_disc_space(vm_attributes: List[Dict]) -> int:
    """Estimate the required disc space for the sandbox"""
    required_space: int = 0
    for vm in vm_attributes:
        required_space += _estimate_box_space_requirements(vm.get("box"))
    return required_space


def verify_available_disc_space(vm_attributes: List[Dict], sandbox_directory: str):
    """Verify if enough disk space is available for the sandbox"""
    available_disc_space: int = _get_available_disc_space(sandbox_directory)
    required_disc_space: int = _get_required_disc_space(vm_attributes)
    if required_disc_space > available_disc_space:
        print("Warning: The available disc space on your system is low. "
              "You may run into issues.")
