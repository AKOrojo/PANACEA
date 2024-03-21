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


def detect_and_print_conflicts(finalized_data_units):
    """
    Detects conflicts within finalized data units based on applied policies and prints them.
    :param finalized_data_units: Dictionary of finalized data units with applied policies.
    """
    for key, du in finalized_data_units.items():
        # Assuming policies are stored in a 'policies' list within each 'du'
        policies = du.get('value', {}).get('pol', [])
        permit_policies = [p for p in policies if p['tp'] == 'positive']
        deny_policies = [p for p in policies if p['tp'] == 'negative']

        # Basic conflict detection: If there are both permit and deny policies
        if permit_policies and deny_policies:
            print(f"Conflict detected in data unit {key}:")
            print(f"Permit Policies: {permit_policies}")
            print(f"Deny Policies: {deny_policies}")
            print(f"Content: {du.get('value', {}).get('V', 'No content available.')}\n")
