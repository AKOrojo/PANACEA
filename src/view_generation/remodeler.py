def remodelerMap(urps):
    """
    Groups Unifying Resource Properties (URPs) by their data unit identifier.

    This function simulates the initial mapping phase of the MapReduce task remodeler,
    organizing URPs based on the data units they belong to. It's the first step in the
    reverse mapping process, preparing URPs for aggregation into structured data units.

    Parameters:
    - urps (list of dict): A list of Unifying Resource Properties, each represented as a dictionary.

    Returns:
    - dict: A dictionary where each key is a data unit identifier and each value is a list
            of URPs belonging to that data unit.
    """

    grouped_urps = {}  # Initialize an empty dictionary to hold grouped URPs.
    for urp_tuple in urps:
        urp_id, urp_value = urp_tuple  # Extract ID and value from each tuple in the list.
        key = urp_value['path'][0]  # Use the first element of the 'path' as the grouping key.
        if key not in grouped_urps:
            grouped_urps[key] = []  # Initialize a new list if key is not already present.
        grouped_urps[key].append(urp_value)  # Append the URPs to the appropriate list.
    return grouped_urps



def r(urpS, key):
    """
    Reduces a set of URPs by a specific key to structure the data unit.

    This function iterates over a set of URPs, organizing and aggregating them into a structured
    data unit based on a specified key. It differentiates between URPs that match the key directly
    and those that do not, handling them accordingly to construct the final data unit.

    Parameters:
    - urpS (list of dict): The set of URPs modeling components of the same data unit.
    - key (str): The identifier key of the referred data unit.

    Returns:
    - dict: The aggregated data unit as a dictionary.
    """
    du = {}  # Initialize the data unit as an empty dictionary.
    tbs = []  # To be structured: List of URPs needing further processing.
    tbp = []  # To be pruned: List of URPs that will be removed after structuring.

    # Iterate over each URP in the set.
    for urp in urpS:
        if urp['path'][-1] == key:  # Check if the URP refers directly to the specified key.
            if 'V' in urp:  # If 'V' is present, use it as the value.
                du[urp['K']] = urp['V']
            else:  # Otherwise, use the 'id' as the value and note it for structuring.
                du[urp['K']] = urp['id']
                tbs.append(urp['id'])
        else:  # For URPs not referring directly to the key.
            if urp['path'][-1] not in du:  # Initialize a nested dictionary if needed.
                du[urp['path'][-1]] = {}
                tbp.append(urp['path'][-1])
            if 'V' in urp:  # Assign 'V' or 'id' to the nested dictionary accordingly.
                du[urp['path'][-1]][urp['K']] = urp['V']
            else:
                du[urp['path'][-1]][urp['K']] = urp['id']
                tbs.append(urp['id'])

    du['tbs'] = tbs  # Add the list of URPs to be structured to the data unit.
    du['tbp'] = tbp  # Add the list of URPs to be pruned to the data unit.
    return du



def f(du):
    """
    Finalizes the data unit by removing specified fields and updating values.

    This function processes the data unit resulting from the `r` function, removing
    unnecessary fields and updating the data unit based on the lists of URPs to be
    structured and pruned.

    Parameters:
    - du (dict): The data unit derived from the execution trace of `r`.

    Returns:
    - dict: The modified version of the data unit.
    """
    # Process each URP marked for structuring.
    for oid in du['tbs']:
        if oid in du:  # Check if the URP exists within the data unit.
            updateDu(du, oid, du[oid])  # Update the data unit accordingly.
            del du[oid]  # Remove the URP after updating.

    # Process each URP marked for pruning.
    for oid in du['tbp']:
        if oid in du:  # Check if the URP exists within the data unit.
            del du[oid]  # Remove the URP.

    # Clean up by removing the lists of URPs to be structured and pruned.
    del du['tbs']
    del du['tbp']
    return du



def updateDu(du, oid, value):
    """
    Recursively updates the data unit, replacing references with actual values.

    This helper function traverses the data unit and replaces any occurrences of
    an object identifier (oid) with the specified value. It supports nested data
    units by recursing into dictionaries.

    Parameters:
    - du (dict): The data unit to be updated.
    - oid (str): The object identifier to be replaced.
    - value (various): The value to replace the object identifier with.

    Note:
    This function modifies the data unit in place.
    """
    for key, val in du.items():
        if isinstance(val, dict):  # If the value is a dictionary, recurse into it.
            updateDu(val, oid, value)
        elif val == oid:  # If the value matches the object identifier, replace it.
            du[key] = value

