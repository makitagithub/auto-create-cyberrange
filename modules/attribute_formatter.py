def _format_and_add(key, value, mappings, device_definition):
    """ Formats and adds the definition of a simple attribute. """

    if (key in mappings['string']):
        device_definition.append(
                'device.' + mappings['string'][key]
                + ' = \"' + str(value) + '\"')
    elif (key in mappings['integer']):
        device_definition.append(
                'device.' + mappings['integer'][key]
                + ' = ' + str(value))
    elif (key in mappings['boolean']):
        device_definition.append(
                'device.' + mappings['boolean'][key]
                + ' = ' + str(value).lower())


def add_simple_commands(device, mappings, device_definition):
    """ Adds definitions of string, integer and boolean vagrant attributes. """

    for key, value in device.items():
        if (key != "name"):
            _format_and_add(key, value, mappings, device_definition)

