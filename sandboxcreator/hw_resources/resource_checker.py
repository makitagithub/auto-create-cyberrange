from pathlib import Path

from sandboxcreator.hw_resources.memory import verify_available_memory
from sandboxcreator.io.reader import Reader


def check_hw_resources(sandbox_directory: str) -> None:
    """Check if the available hw resources can handle the given sandbox"""
    vagrantfile_path: Path = Path(sandbox_directory).joinpath("Vagrantfile")
    if not vagrantfile_path.is_file():
        return
    vagrantfile: str = Reader.get_textfile(vagrantfile_path)
    verify_available_memory(vagrantfile)
