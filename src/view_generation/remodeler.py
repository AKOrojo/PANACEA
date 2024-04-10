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

    grouped_urps = {}
    for urp in urps:
        key = urp['value']['path'][0]
        if key not in grouped_urps:
            grouped_urps[key] = []
        grouped_urps[key].append(urp)
    return grouped_urps


def setField(du, key, value):
    """
    Sets a field in the data unit 'du', handling hierarchical structures and placeholders.

    Parameters:
    - du: The data unit being constructed.
    - key: The field key to set in 'du'.
    - value: The value for the field key.
    """
    du[key] = value


def last_path(path):
    return path[-1]


def reduce_by_key(urpS, key):
    """
    Aggregates URPs into a structured data unit based on the specified key, handling hierarchical
    structures and placeholders.

    Parameters:
    - urpS: A list of URPs belonging to the same data unit.
    - key: The identifier key of the data unit being constructed.

    Returns:
    - A structured data unit with fields set according to the URPs, including resolved placeholders.
    """
    du = {}
    tbs = []
    tbp = []

    for urp in urpS:
        urp_id = urp['value']['id']
        path = urp['value']['path']
        K = urp['value'].get('K')
        V = urp['value'].get('V', None)
        if last_path(path) == key:
            if isinstance(V, (int, float, bool, str)):
                setField(du, K, V)
            else:
                setField(du, K, V)
                tbs.append(urp_id)
        else:
            if last_path(path) not in urp:
                setField(du, last_path(path), {})
                tbp.append(last_path(path))
            if isinstance(V, (int, float, bool, str)):
                setField(du, K, V)
            else:
                setField(du, K, urp_id)
                tbs.append(urp_id)

    setField(du, "tbs", tbs)
    setField(du, "tbp", tbp)

    return du


def updateDu(du, oid, replacement_value):
    """
    Updates the data unit 'du' by replacing the placeholder identified by 'oid' with 'replacement_value'.
    This function traverses 'du' to find 'oid' and replaces it.
    """
    for key, value in du.items():
        if key == oid:
            du[key] = replacement_value
            return True
        elif isinstance(value, dict):
            if updateDu(value, oid, replacement_value):
                return True
    return False


def delField(du, field):
    """
    Deletes a field from 'du'. If the field is nested, navigates to the correct position to delete.
    """
    if field in du:
        del du[field]
    else:
        for value in du.values():
            if isinstance(value, dict):
                delField(value, field)


def finalize(du):
    """
    Finalizes the data unit by resolving placeholders and removing temporary structures.

    Parameters:
    - du: The data unit being finalized.
    """
    if 'tbs' not in du or 'tbp' not in du:
        return du

    # Resolve placeholders specified within 'tbs'
    for oid in du['tbs']:
        if oid in du:
            replacement_value = du[oid]
            updateDu(du, oid, replacement_value)

    # Remove fields specified in 'tbp'
    for oid in du['tbp']:
        delField(du, oid)

    # Clean up 'tbs' and 'tbp' from 'du'
    del du['tbs']
    del du['tbp']

    return du
