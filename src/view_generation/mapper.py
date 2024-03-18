def set_field(du, key, value):
    """
    Sets a field in the data unit. Creates nested dictionaries if necessary.
    """
    keys = key.split('.')
    for k in keys[:-1]:
        du = du.setdefault(k, {})
    du[keys[-1]] = value


def r(urpS, key):
    """
    The reduce by key function of remodeler. Aggregates URPs into a data unit.
    """
    du = {}
    tbs = []
    tbp = []

    for urp in urpS:
        urp_value = urp['value']
        urp_path = urp_value['path']
        urp_key = 'K' in urp_value and urp_value['K']
        urp_value = 'V' in urp_value and urp_value['V']

        if urp_path[-1] == key:
            if urp_value:
                set_field(du, urp_key, urp_value)
            else:
                set_field(du, urp_key, urp['id'])
                tbs.append(urp['id'])
        else:
            # Nested components
            last_path_key = urp_path[-1]
            if not urp_value:
                set_field(du, last_path_key, None)
                tbp.append(last_path_key)

            nested_key = '.'.join(urp_path[:-1] + [urp_key])
            set_field(du, nested_key, urp_value if urp_value else urp['id'])
            if not urp_value:
                tbs.append(urp['id'])

    du['tbs'] = tbs
    du['tbp'] = tbp

    return du


def update_du(du, oid, value):
    """
    Recursively updates the data unit to replace placeholders with actual values.
    """
    for k, v in du.items():
        if isinstance(v, dict):
            update_du(v, oid, value)
        elif k == oid:
            du[k] = value


def del_field(du, oid):
    """
    Deletes a field from the data unit, searching recursively.
    """
    to_delete = []
    for k, v in du.items():
        if isinstance(v, dict):
            del_field(v, oid)
        elif k == oid:
            to_delete.append(k)
    for k in to_delete:
        del du[k]


def f(du):
    """
    Finalize the data unit by replacing placeholders and cleaning up.
    """
    for oid in du.get('tbs', []):
        if oid in du:
            update_du(du, oid, du[oid])
            del_field(du, oid)

    for oid in du.get('tbp', []):
        del_field(du, oid)

    # Clean up temporary fields
    del_field(du, 'tbs')
    del_field(du, 'tbp')

    return du
