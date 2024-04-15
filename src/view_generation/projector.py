import re
from src.view_generation.remodeler import remodelerMap


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
        decisions['default'] = 'permit'
        return decisions

    if 'subject' not in arc or 'aip' not in arc['subject']:
        decisions['default'] = 'deny'
        return decisions

    # Iterate over each metadata and policy set in the URP
    for i in range(len(urp['meta'])):
        meta = urp['meta'][i]
        pol = urp['pol'][i]

        if pol['exp'] == "s.ap in meta.aip":
            if arc['subject']['aip'] in meta['aip']:
                set_decision = 'permit' if pol['tp'] == 'positive' else 'deny'
            else:
                set_decision = 'deny' if pol['tp'] == 'positive' else 'permit'
        elif pol['exp'] == "s.ap not in meta.aip":
            if arc['subject']['aip'] not in meta['aip']:
                set_decision = 'permit' if pol['tp'] == 'positive' else 'deny'
            else:
                set_decision = 'deny' if pol['tp'] == 'positive' else 'permit'
        else:
            set_decision = 'deny'

        decisions[f"set_{i}"] = set_decision

        return decisions


def combinePs(decisions, co):
    """
    Combines the decisions from multiple policies based on the specified combining option.

    Parameters:
    - decisions (list): A list of access decisions ('permit', 'deny', or 'notApplicable').
    - co (str): The combining option ('any' or 'all').

    Returns:
    - str: The combined access decision ('permit', 'deny', or 'notApplicable').
    """
    if co == 'any':
        if 'permit' in decisions:
            return 'permit'
        elif 'deny' in decisions:
            return 'deny'

    elif co == 'all':
        if 'deny' in decisions:
            return 'deny'
        elif all(decision == 'permit' for decision in decisions):
            return 'permit'


def conflictRes(Ps, crs, arc):
    """
    Resolves conflicts between positive and negative policies Ps based on the conflict resolution strategy crs.

    Parameters:
    - Ps (list of dict): A list of policy objects, containing both positive and negative policy predicates.
        - Each policy object should have the following structure:
            {
                'exp': 'expression to evaluate',
                'tp': 'positive' or 'negative'
            }
    - crs (str): The conflict resolution strategy, either 'denials take precedence' or 'permissions take precedence'.
    - arc (dict): The access request context.

    Returns:
    - bool: The final decision after resolving conflicts between positive and negative policies.
    """
    positive_decisions = []
    negative_decisions = []

    # Evaluate each policy predicate and categorize the decisions
    for p in Ps:
        decision = evaluate(p, arc)
        if p['tp'] == 'positive':
            positive_decisions.append(decision)
        else:
            negative_decisions.append(decision)

    # Resolve conflicts based on the conflict resolution strategy
    if crs == 'denials take precedence':
        # If any negative decision is True, return False
        return not any(negative_decisions)
    elif crs == 'permissions take precedence':
        # If any positive decision is True, return True
        return any(positive_decisions)
    else:
        # Return False if the conflict resolution strategy is not supported
        return False


def propagateDCG(du, cgl1, ppc):
    """
   Propagates decisions related to coarse-grained resources at level 1 (DCG L1) to the data unit du.

   Parameters:
   - du (dict): The data unit object.
   - cgl1 (dict): The decisions related to coarse-grained resources at level 1.
   - ppc (str): The policy propagation criterion, one of 'no propagation', 'no overriding', or 'most specific overrides'.

   Returns:
   - dict: The updated data unit du with propagated decisions.
   """
    # Implement the logic to propagate the DCG L1 decisions to the data unit du
    # based on the policy propagation criterion
    # Update the 'pol' and 'meta' fields of du accordingly
    # Return the updated data unit
    pass


def propagateFCG(du, cgl2, ppc):
    """
   Propagates decisions related to coarse-grained resources at level 2 (FCG L2) to the data unit du.

   Parameters:
   - du (dict): The data unit object.
   - cgl2 (dict): The decisions related to coarse-grained resources at level 2.
   - ppc (str): The policy propagation criterion, one of 'no propagation', 'no overriding', or 'most specific overrides'.

   Returns:
   - dict: The updated data unit du with propagated decisions.
   """
    # Implement the logic to propagate the DCG L2 decisions to the data unit du
    # based on the policy propagation criterion
    # Update the 'pol' and 'meta' fields of du accordingly
    # Return the updated data unit
    pass


def updateDu(du, arc):
    """
   Updates the data unit du based on the access request context arc.

   Parameters:
   - du (dict): The data unit object.
   - arc (dict): The access request context, containing parameters like subject and environment.

   Returns:
   - dict: The updated data unit du with authorized and unauthorized data marked.
   """
    # Implement the logic to update the data unit du based on the access request context arc
    # Identify the authorized and unauthorized data within du and mark them accordingly
    # Return the updated data unit
    pass


def projector(urps, co, crs, arc):
    """
    Applies the MapReduce task projector to the given URPs.

    Parameters:
    - urps (list of dict): A list of Unifying Resource Properties.
    - co (str): The combining option, either 'any' or 'all'.
    - crs (str): The conflict resolution strategy, either 'denials take precedence' or 'permissions take precedence'.
    - arc (dict): The access request context.

    Returns:
    - dict: A dictionary containing the results of the MapReduce task projector.
    """
    # Apply the map function m to the URPs
    grouped_urps = remodelerMap(urps)

    # Apply to evaluate, combinePs, and conflictRes functions to the grouped URPs
    results = {}
    # for key, urps_list in grouped_urps.items():
    #     results[key] = {'combined_decision': combined_decision, 'resolved_decision': resolved_decision, 'evaluation_decision': evaluation_decision}

    return results


def handleSP(fdr1, tdr2, ppc, crs, st):
    """Handle specific policy propagation cases."""
    if ppc == "most-specific-overrides":
        return tdr2 if tdr2 else fdr1
    elif ppc == "no-overriding":
        if tdr2:
            if crs == "denials-take-precedence":
                return "deny" if "deny" in [fdr1, tdr2] else "permit"
            else:
                return "permit" if "permit" in [fdr1, tdr2] else "deny"
        else:
            return fdr1
    elif ppc == "no-propagation":
        return tdr2 if tdr2 else ("permit" if st == "open" else "deny")


def propagateDCG(cgl1, cgl2, dcgl1, dcgl2, crs, ppc, st):
    """Propagate decisions from coarse-grained resources."""
    dec = "permit" if dcgl1 == "permit" or st == "open" else "deny"
    unauthCGR = []
    if dec == "deny":
        unauthCGR.append(cgl1)
        if cgl2:
            dec = handleSP(dec, dcgl2, ppc, crs, st)
            if dec == "deny":
                unauthCGR.append(cgl2)
    return dec, unauthCGR


def apply_policies_to_du(du, ppc, crs, st):
    """Apply policies to a single data unit and its components."""
    fdr1 = "permit"
    tdr2 = du.get("policy_decision", None)

    final_decision = handleSP(fdr1, tdr2, ppc, crs, st)

    du["access_decision"] = final_decision

    for key, value in du.items():
        if isinstance(value, dict):
            apply_policies_to_du(value, ppc, crs, st)

    return du
