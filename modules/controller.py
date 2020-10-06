"""Contains functions for controller creation."""


CONTROLLER_NAME = "controller"


def _are_controller_parameters_free(definitions):
    """Check if controller parameters are not already taken."""
    for host in definitions["hosts"]:
        if host["name"] == CONTROLLER_NAME:
            return False
        # TODO add other parameters

    return True


def create_controller(definitions):
    """Add the definition of controller to definitions.

    :param definitions: device definition structure
    """

    # TODO this should be later moved to input check
    if not _are_controller_parameters_free(definitions):
        raise ValueError("A device with the same name as border router "
                         "already exists.")

    return
