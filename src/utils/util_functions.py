def print_urp(urp):
    """
    Prints a Unifying Resource Property (URP) in a structured and readable format.

    :param urp: The URP dictionary to print.
    """

    if 'value' in urp:
        value_str = "{\n"
        value_str += f"  'path': {urp['value'].get('path', [])},\n"
        value_str += f"  'id': '{urp['value'].get('id', 'Unknown')}',\n"
        value_str += f"  'K': '{urp['value'].get('K', 'Unknown')}',\n"
        if 'V' in urp['value']:
            value_str += f"  'V': '{urp['value'].get('V', 'Unknown')}'\n"
        value_str += "}"
        print(f"{{'_id': '{urp.get('_id', 'Unknown')}',\n'value': {value_str}}}\n")
    else:
        # Fallback
        print(f"URP does not have the expected structure: {urp}")

