from src.access_control_view.remodeler import updateDu

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

    if 'meta' not in urp or not urp['meta'] or 'pol' not in urp or not urp['pol']:
        decisions['default'] = {'decision': 'permit', 'tp': 'positive'}
        return decisions

    if 'subject' not in arc or 'attributes' not in arc['subject'] or 'department' not in arc['subject']['attributes']:
        decisions['default'] = {'decision': 'deny', 'tp': 'negative'}
        return decisions

    subject_department = arc['subject']['attributes']['department']

    # Iterate over each policy set in the URP
    for i, pol in enumerate(urp['pol']):
        meta = urp['meta']
        if pol['exp'] == "s.ap in meta.aip":
            if subject_department in meta['aip']:
                set_decision = {'decision': 'permit', 'tp': pol['tp']}
            else:
                set_decision = {'decision': 'deny', 'tp': pol['tp']}
        elif pol['exp'] == "s.ap in meta.pip":
            if subject_department in meta['pip']:
                set_decision = {'decision': 'deny', 'tp': pol['tp']}
            else:
                set_decision = {'decision': 'permit', 'tp': pol['tp']}
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
                'K': urp['K'],
                'path': urp['path'],
                'psa': [policy['exp'] for policy in urp['pol'] if policy['tp'] == 'positive'],
                'psp': [policy['exp'] for policy in urp['pol'] if policy['tp'] == 'negative']
            })

    du['tbs'] = tbs  # Add the list of URPs to be structured to the data unit.
    du['tbp'] = tbp  # Add the list of URPs to be pruned to the data unit.
    du['meta'] = meta  # Add the security metadata to the data unit.
    du['pol'] = pol  # Add the policies to the data unit.

    return du


def propagateDCG(du, arc, co, crs, ppc, st):
    """
    Propagates access decisions from coarse-grained resources to the data unit.

    Parameters:
    - du (dict): The data unit.
    - arc (dict): The access request context.
    - co (str): The combining option.
    - crs (str): The conflict resolution strategy.
    - ppc (str): The policy propagation criterion.
    - st (str): The system type.

    Returns:
    - str: The propagated access decision for the data unit.
    """
    global dcgl, cgl

    dec = None
    for level in sorted(dcgl.keys(), reverse=True):
        if level in cgl and du['_id'] in cgl[level]:
            cgr_id = list(cgl[level][du['_id']].keys())[0]
            if cgr_id in dcgl[level][du['_id']]:
                cgr_decision = dcgl[level][du['_id']][cgr_id]
                if dec is None:
                    dec = cgr_decision
                else:
                    dec = handleSP(dec, cgr_decision, ppc, crs, st)

    return dec


def handleSP(fdr1, tdr2, ppc, crs, st):
    """
    Derives the final access decision for a resource based on the propagation criterion,
    conflict resolution strategy, and system type.

    Parameters:
    - fdr1 (str): The access decision of the parent resource.
    - tdr2 (str): The temporary access decision of the current resource.
    - ppc (str): The policy propagation criterion ('most-specific-overrides', 'no-overriding', 'no-propagation').
    - crs (str): The conflict resolution strategy ('denials-take-precedence', 'permissions-take-precedence').
    - st (str): The system type ('open', 'closed').

    Returns:
    - str: The final access decision for the current resource.
    """
    fdr2 = None

    if ppc == 'most-specific-overrides':
        if tdr2 is None:
            fdr2 = fdr1
        else:
            fdr2 = tdr2
    elif ppc == 'no-overriding':
        if tdr2 is None:
            fdr2 = fdr1
        else:
            if crs == 'denials-take-precedence':
                fdr2 = 'deny' if fdr1 == 'deny' or tdr2 == 'deny' else 'permit'
            elif crs == 'permissions-take-precedence':
                fdr2 = 'permit' if fdr1 == 'permit' or tdr2 == 'permit' else 'deny'
    elif ppc == 'no-propagation':
        if tdr2 is not None:
            fdr2 = tdr2
        else:
            if st == 'open':
                fdr2 = 'permit'
            elif st == 'closed':
                fdr2 = 'deny'

    return fdr2


def propagateDFG(du, decision, ppc, crs, st):
    """
    Propagates access decisions within the data unit using depth-first traversal.

    Parameters:
    - du (dict): The data unit.
    - decision (str): The access decision to propagate.
    - ppc (str): The policy propagation criterion.
    - crs (str): The conflict resolution strategy.
    - st (str): The system type.
    """

    def dfs(node, path, dec):
        if isinstance(node, dict):
            if 'id' in node and 'path' in node:
                node_path = node['path']
                if any(item['path'] == node_path for item in du['authS']):
                    temp_dec = 'permit'
                elif any(item['path'] == node_path for item in du['prohS']):
                    temp_dec = 'deny'
                else:
                    temp_dec = None

                final_dec = handleSP(dec, temp_dec, ppc, crs, st)
                if final_dec == 'deny':
                    du.setdefault('unauthS', []).append({'id': node['id'], 'path': node_path})
                dec = final_dec

            for key, value in node.items():
                dfs(value, path + [key], dec)
        elif isinstance(node, list):
            for item in node:
                dfs(item, path, dec)

    dfs(dict(du), [], decision)  # Create a copy of the data unit dictionary


def generateView(du):
    """
    Generates the view of the data unit by marking unauthorized components.

    Parameters:
    - du (dict): The data unit.

    Returns:
    - dict: The view of the data unit with unauthorized components marked.
    """

    def mark_unauthorized(node, path):
        if isinstance(node, dict):
            if 'id' in node and 'path' in node:
                node_path = node['path']
                if any(item['path'] == node_path for item in du.get('unauthS', [])):
                    return f"[UNAUTHORIZED (id: {node.get('id', '')}, path: {node.get('path', '')})]"

            return {key: mark_unauthorized(value, path + [key]) for key, value in node.items()}
        elif isinstance(node, list):
            return [mark_unauthorized(item, path) for item in node]
        else:
            return node

    view = mark_unauthorized(du, [])
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

    # Remove temporary fields (tbs and tbp)
    if 'tbs' in du:
        for oid in du['tbs']:
            if oid in du:
                updateDu(du, oid, du[oid])
                del du[oid]
        del du['tbs']

    if 'tbp' in du:
        for oid in du['tbp']:
            if oid in du:
                del du[oid]
        del du['tbp']

    # Policy Composition
    authS = []
    prohS = []

    for p in du.get('pol', []):
        obj = {'id': p['id'], 'path': p['path']}
        if 'meta' in du:
            for meta in du['meta']:
                if meta['id'] == p['id'] and meta['path'] == p['path']:
                    obj.update(meta['psSet'])

        psa_decisions = [{'set_0': {'decision': 'permit', 'tp': 'positive'}}] if not p['psa'] else [
            evaluate({'meta': obj, 'pol': [{'exp': psa, 'tp': 'positive'}]}, arc) for psa in p['psa']]
        psp_decisions = [{'set_0': {'decision': 'permit', 'tp': 'negative'}}] if not p['psa'] else [
            evaluate({'meta': obj, 'pol': [{'exp': psp, 'tp': 'negative'}]}, arc) for psp in p['psp']]

        combined_psa = combinePs({f'set_{i}': d['set_0'] for i, d in enumerate(psa_decisions)}, co)
        combined_psp = combinePs({f'set_{i}': d['set_0'] for i, d in enumerate(psp_decisions)}, co)

        decision = conflictRes({'positive': combined_psa.get('positive'), 'negative': combined_psp.get('negative')},
                               crs)

        if decision == 'permit':
            authS.append({'id': p['id'], 'path': p['path']})
        elif decision == 'deny':
            prohS.append({'id': p['id'], 'path': p['path']})
        else:
            print("no decision")

    du['authS'] = authS
    du['prohS'] = prohS

    # Policy Propagation
    propagated_decision = propagateDCG(du, arc, co, crs, ppc, st)
    propagateDFG(du, propagated_decision, ppc, crs, st)

    # View Generation
    view = generateView(du)

    return view
