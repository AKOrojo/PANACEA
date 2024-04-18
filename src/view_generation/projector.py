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
    meta = []  # List to store security metadata.
    pol = []  # List to store policies.

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

        # Collect security metadata and policies from the URP.
        if 'meta' in urp:
            meta.append({
                'id': urp['id'],
                'path': urp['path'],
                'psSet': urp['meta']
            })
        if 'pol' in urp:
            pol.append({
                'id': urp['id'],
                'path': urp['path'],
                'psa': [policy['exp'] for policy in urp['pol'] if policy['tp'] == 'positive'],
                'psp': [policy['exp'] for policy in urp['pol'] if policy['tp'] == 'negative']
            })

    du['tbs'] = tbs  # Add the list of URPs to be structured to the data unit.
    du['tbp'] = tbp  # Add the list of URPs to be pruned to the data unit.
    du['meta'] = meta  # Add the security metadata to the data unit.
    du['pol'] = pol  # Add the policies to the data unit.

    return du


def handleSP(fdr1, tdr2, ppc, crs, st):
    """
    Derives the final access decision for a resource based on the temporary decision
    and the decision of the parent resource.

    Parameters:
    - fdr1 (str): The access decision derived for the parent resource.
    - tdr2 (str): The temporary decision derived for the current resource.
    - ppc (str): The policy propagation criterion ('most-specific-overrides', 'no-overriding', 'no-propagation').
    - crs (str): The conflict resolution strategy ('denials-take-precedence', 'permissions-take-precedence').
    - st (str): The system type ('open', 'closed').

    Returns:
    - str: The final access decision for the current resource.
    """
    fdr2 = None
    if ppc == 'most-specific-overrides':
        if tdr2 is None:
            return fdr1
        else:
            return tdr2
    elif ppc == 'no-overriding':
        if tdr2 is None:
            return fdr1
        else:
            if crs == 'denials-take-precedence':
                return 'deny' if fdr1 == 'deny' or tdr2 == 'deny' else 'permit'
            elif crs == 'permissions-take-precedence':
                return 'permit' if fdr1 == 'permit' or tdr2 == 'permit' else 'deny'
    elif ppc == 'no-propagation':
        if tdr2 is not None:
            return tdr2
        else:
            return 'permit' if st == 'open' else 'deny'
    return fdr2


def propagateDCG(du, cgl_values, dcgl_values, crs, ppc, st):
    """
    Derives the decision to be propagated to the data unit from the access decisions
    taken during the mapping phase for the coarse-grained resources that include the data unit.

    Parameters:
    - du (dict): The data unit.
    - cgl_values (list): The list of coarse-grained resource identifiers at each level.
    - dcgl_values (list): The list of access decisions for coarse-grained resources at each level.
    - crs (str): The conflict resolution strategy ('denials-take-precedence', 'permissions-take-precedence').
    - ppc (str): The policy propagation criterion ('most-specific-overrides', 'no-overriding', 'no-propagation').
    - st (str): The system type ('open', 'closed').

    Returns:
    - str: The access decision to be propagated to the data unit.
    """
    dec = None
    if dcgl1 == 'permit' or dcgl1 == 'deny':
        dec = dcgl1
    else:
        dec = 'permit' if st == 'open' else 'deny'
    if dec == 'deny':
        du.setdefault('unauthCGR', []).append(cgl1)
    if cgl2 is not None:
        dec = handleSP(dec, dcgl2, ppc, crs, st)
        if dec == 'deny':
            du.setdefault('unauthCGR', []).append(cgl2)
    return dec


def propagateDFG(du, r, d, ppc, crs, st):
    """
    Propagates the access decision within the data unit through a depth-first visit of the data unit's tree structure.

    Parameters:
    - du (dict): The data unit.
    - r (dict): The current resource in the data unit's tree structure.
    - d (str): The access decision of the parent resource.
    - ppc (str): The policy propagation criterion ('most-specific-overrides', 'no-overriding', 'no-propagation').
    - crs (str): The conflict resolution strategy ('denials-take-precedence', 'permissions-take-precedence').
    - st (str): The system type ('open', 'closed').

    Returns:
    - None
    """
    td = r.get('authS', []) + r.get('prohS', []) + r.get('undefS', [])
    td = td[0] if td else None
    fd = handleSP(d, td, ppc, crs, st)
    if fd == 'deny':
        du.setdefault('prohR', []).append(r['path'])
    for child in r.values():
        if isinstance(child, dict):
            propagateDFG(du, child, fd, ppc, crs, st)


def generateView(du):
    """
    Generates a view of the data unit by marking unauthorized components.

    Parameters:
    - du (dict): The data unit.

    Returns:
    - dict: The view of the data unit with unauthorized components marked.
    """
    view = {}
    for k, v in du.items():
        if isinstance(v, dict):
            view[k] = generateView(v)
        elif k not in ['unauthCGR', 'prohR']:
            view[k] = v
    if du.get('prohR'):
        view['unauthorized'] = True
    return view


def projector_f(du, arc, co, crs, ppc, st):
    """
    Finalizes the data unit by removing specified fields, updating values, performing policy composition,
    policy propagation, and generating the view of the data unit.

    Parameters:
    - du (dict): The data unit derived from the execution trace of `r`.
    - arc (dict): An access request context containing subject attributes.
    - co (str): The combining option ('any' or 'all').
    - crs (str): The conflict resolution strategy ('denials-take-precedence', 'permissions-take-precedence').
    - ppc (str): The policy propagation criterion ('most-specific-overrides', 'no-overriding', 'no-propagation').
    - st (str): The system type ('open', 'closed').

    Returns:
    - dict: The view of the data unit with authorized and unauthorized components.
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

    # Policy composition task
    for p in du.get('pol', []):
        # Derive the protection object obj for policy p
        obj = {k: v for k, v in du.items() if k in p['path']}
        obj.update({m['id']: m['psSet'] for m in du.get('meta', []) if m['id'] in p['path']})

        # Evaluate policies for the protection object
        access_decision = evaluate(obj, arc)

        # Combine positive and negative policies using combinePs and conflictRes
        combined_decision = combinePs(access_decision, co)
        temp_decision = conflictRes(combined_decision, crs)

        # Keep track of temporary decisions
        if temp_decision == 'permit':
            du.setdefault('authS', []).append(p['path'])
        elif temp_decision == 'deny':
            du.setdefault('prohS', []).append(p['path'])
        else:
            du.setdefault('undefS', []).append(p['path'])

    cgl_values = []
    dcgl_values = []

    for level in range(1, len(du['path']) + 1):
        key = du['path'][level - 1]
        if level in cgl and key in cgl[level]:
            cgl_value = cgl[level][key].get(du['id'])
            dcgl_value = dcgl[level][key].get(du['id'])
            cgl_values.append(cgl_value)
            dcgl_values.append(dcgl_value)
        else:
            cgl_values.append(None)
            dcgl_values.append(None)

    dec = propagateDCG(du, cgl_values, dcgl_values, crs, ppc, st)

    # Propagate decisions within the data unit
    propagateDFG(du, du, dec, ppc, crs, st)

    # View generation task
    view = generateView(du)

    return view
