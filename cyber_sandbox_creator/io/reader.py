import yaml

from pathlib import Path
from typing import Union, List, Dict


class Reader:
    """Static methods for reading from files"""

    @staticmethod
    def open_yaml(file_path: Path) -> Union[List, Dict]:
        """Open a yaml file and return its content"""
        try:
            with file_path.open() as input_file:
                return yaml.safe_load(input_file)
        except yaml.YAMLError:
            raise IOError(f"Could not parse yaml file {file_path}.")
        except IOError:
            raise IOError(f"Could not open yaml file {file_path}.")
