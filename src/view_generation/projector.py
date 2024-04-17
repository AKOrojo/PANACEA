from src.view_generation.remodeler import updateDu

dcgl = {}
cgl = {}

def evaluate(urp, arc):
    """
    Evaluates the access control policies specified for a Unifying Resource Property (URP)
    against the given access request context.

    Parameters:
    - urp (dict): A Unifying Resource Property represented as a dictionary.
    - arc (dict): An access request context containing subject attributes.

    Returns:
    - dict: A dictionary containing the access decisions for different metadata and policy sets.
    """
    decisions = {}

    if 'meta' not in urp or 'pol' not in urp:
        decisions['default'] = {'decision': 'permit', 'tp': 'positive'}
        return decisions

    if 'subject' not in arc or 'aip' not in arc['subject']:
        decisions['default'] = {'decision': 'deny', 'tp': 'negative'}
        return decisions

    # Iterate over each metadata and policy set in the URP
    for i in range(len(urp['meta'])):
        meta = urp['meta'][i]
        pol = urp['pol'][i]

        if pol['exp'] == "s.ap in meta.aip":
            if arc['subject']['aip'] in meta['aip']:
                set_decision = {'decision': 'permit', 'tp': pol['tp']}
            else:
                set_decision = {'decision': 'deny', 'tp': pol['tp']}
        elif pol['exp'] == "s.ap not in meta.aip":
            if arc['subject']['aip'] not in meta['aip']:
                set_decision = {'decision': 'permit', 'tp': pol['tp']}
            else:
                set_decision = {'decision': 'deny', 'tp': pol['tp']}
        else:
            set_decision = {'decision': 'deny', 'tp': 'negative'}

        decisions[f"set_{i}"] = set_decision

    return decisions


def combinePs(decisions, co):
    """
    Combines the decisions from multiple policies based on the specified combining option.

    Parameters:
    - decisions (dict): A dictionary of access decisions, where the key is the set identifier
                        and the value is a dictionary containing the decision ('permit' or 'deny')
                        and the policy type ('positive' or 'negative').
    - co (str): The combining option ('any' or 'all').

    Returns:
    - dict: A dictionary containing the combined access decision for positive and negative policy types.
    """
    combined_decision = {}

    if co == 'any':
        for decision in decisions.values():
            if decision['tp'] not in combined_decision:
                combined_decision[decision['tp']] = decision['decision']
            elif decision['decision'] == 'permit':
                combined_decision[decision['tp']] = 'permit'
    elif co == 'all':
        for decision in decisions.values():
            if decision['tp'] not in combined_decision:
                combined_decision[decision['tp']] = decision['decision']
            elif decision['decision'] == 'deny':
                combined_decision[decision['tp']] = 'deny'

    return combined_decision


def conflictRes(combined_decision, crs):
    """
    Resolves conflicts between positive and negative policy decisions based on the specified
    conflict resolution strategy.

    Parameters:
    - combined_decision (dict): A dictionary containing the combined access decision for positive
                                and negative policy types.
    - crs (str): The conflict resolution strategy ('denials take precedence' or 'permissions take precedence').

    Returns:
    - str: The final access decision after resolving conflicts.
    """
    if crs == 'denials-take-precedence':
        if 'negative' in combined_decision:
            if combined_decision['negative'] == 'deny':
                return 'deny'
            elif 'positive' in combined_decision:
                return combined_decision['positive']
        elif 'positive' in combined_decision:
            return combined_decision['positive']
    elif crs == 'permissions-take-precedence':
        if 'positive' in combined_decision:
            if combined_decision['positive'] == 'permit':
                return 'permit'
            elif 'negative' in combined_decision:
                return combined_decision['negative']
        elif 'negative' in combined_decision:
            return combined_decision['negative']

    return None


def projector_m(urps, arc, co, crs):
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

    for key, urp_group in grouped_urps.items():
        for urp in urp_group:
            if 'V' not in urp:  # Check if URP represents a coarse-grained resource
                access_decision = evaluate(urp, arc)
                urp['access_decision'] = access_decision
                combined_decision = combinePs(access_decision, co)
                urp['combined_decision'] = combined_decision
                conflict_resolution = conflictRes(combined_decision, crs)
                urp['conflict_resolution'] = conflict_resolution

                # Keep track of derived decisions for coarse-grained resources
                level = len(urp['path'])
                global dcgl, cgl
                if level not in dcgl:
                    dcgl[level] = {}
                    cgl[level] = {}
                if key not in dcgl[level]:
                    dcgl[level][key] = {}
                    cgl[level][key] = {}
                dcgl[level][key][urp['id']] = conflict_resolution
                cgl[level][key][urp['id']] = urp['K']
            else:
                access_decision = evaluate(urp, arc)
                urp['access_decision'] = access_decision
                combined_decision = combinePs(access_decision, co)
                urp['combined_decision'] = combined_decision
                conflict_resolution = conflictRes(combined_decision, crs)
                urp['conflict_resolution'] = conflict_resolution

    return grouped_urps


def projector_r(urpS, key):
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


def projector_f(du):
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
