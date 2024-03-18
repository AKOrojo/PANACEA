def evaluate(policy, arc):
    """
    Evaluates a policy against an access request context.

    Args:
        policy (dict): A policy dict with a 'condition' key. The 'condition' key is expected
                       to be a function that takes an access request context as its argument
                       and returns True if the policy's condition is met, False otherwise.
        arc (dict): An access request context represented as a dictionary.

    Returns:
        bool: True if the policy's condition is met under the given arc, False otherwise.
    """
    if 'condition' in policy and callable(policy['condition']):
        return policy['condition'](arc)
    else:
        return False


def combine_policies(evaluated_policies, co):
    """
    Combines evaluated policies based on the specified combining option.

    Args:
        evaluated_policies (list of bool): A list where each element represents the result
                                           of evaluating a policy (True for permit, False for deny).
        co (str): The combining option, either 'AND' or 'OR'.

    Returns:
        bool: The combined result of the policies. True if access is permitted based on the
              combining option, False otherwise.
    """
    if co == "AND":
        return all(evaluated_policies)
    elif co == "OR":
        return any(evaluated_policies)
    else:
        print(f"Unknown combining option: {co}. Defaulting to deny access.")
        return False


def resolve_conflict(combined_decision, crs):
    """
    Resolves conflicts among combined policy decisions based on the specified conflict
    resolution strategy.

    Args:
        combined_decision (bool): The result of combining evaluated policies. True if access
                                  is permitted, False otherwise.
        crs (str): The conflict resolution strategy, either 'deny-overrides' or 'permit-overrides'.

    Returns:
        bool: The final access decision after applying the conflict resolution strategy.
    """

    if crs == "deny-overrides":
        return not combined_decision

    elif crs == "permit-overrides":
        return combined_decision

    else:
        print(f"Unknown conflict resolution strategy: {crs}. Defaulting to deny access.")
        return False


def map_phase(dr_star, arc, co, crs):
    evaluated_policies = [evaluate(policy, arc) for policy in dr_star['policies']]
    combined_decision = combine_policies(evaluated_policies, co)
    conflict_resolved_decision = resolve_conflict(combined_decision, crs)
    return conflict_resolved_decision


def r(dr_star, decision):
    """
    Restructures the data resource model based on the policy decision.

    Args:
        dr_star (dict): The unifying resource model representing a data resource with embedded policies.
        decision (bool): The overall policy decision indicating whether access is permitted or not.

    Returns:
        dict: A data unit structured according to the policy decision.
    """
    # Conceptual example: Filter data based on decision
    if decision:
        # If access is permitted, return the data as is or with minimal filtering
        return dr_star
    else:
        # If access is denied, filter out sensitive parts of the data
        return {key: val for key, val in dr_star.items() if not key.startswith("sensitive_")}


def f(du):
    """
    Finalizes the data unit by applying transformations and cleaning up based on policy decisions.

    Args:
        du (dict): The data unit to be finalized, potentially containing placeholders or markers for further processing.

    Returns:
        dict: The finalized data unit, ready for presentation or further processing.
    """
    du_cleaned = {key: val for key, val in du.items() if not key.startswith("temp_")}

    for key, val in du_cleaned.items():
        if "anonymize_" in key:
            du_cleaned[key] = "*****"

    return du_cleaned


def reduce_phase(dr_star, decision):
    du = r(dr_star, decision)
    return du


def finalize_phase(du, ppc, st):
    finalized_du = f(du)
    return finalized_du


def generate_view(finalized_du, decision):
    return finalized_du


def projector(dr_star, co, crs, ppc, st, arc):
    decision = map_phase(dr_star, arc, co, crs)
    du = reduce_phase(dr_star, decision)
    finalized_du = finalize_phase(du, ppc, st)
    return generate_view(finalized_du, decision)


def handleSP(fdr1, tdr2, ppc, crs, st):
    fdr2 = None
    if ppc == "most-specific-overrides":
        fdr2 = fdr1 if tdr2 is None else tdr2
    elif ppc == "no-overriding":
        if tdr2 is None:
            fdr2 = fdr1
        else:
            if crs == "denials-take-precedence":
                fdr2 = fdr1 and tdr2
            elif crs == "permissions-take-precedence":
                fdr2 = fdr1 or tdr2
    elif ppc == "no-propagation":
        if tdr2 is not None:
            fdr2 = tdr2
        else:
            fdr2 = True if st == "open" else False

    return fdr2


def propagateDCG(cgl1, cgl2, dcgl1, dcgl2, crs, ppc, st):

    unauthCGR = []

    if dcgl1 in ["permit", "deny"]:
        dec = True if dcgl1 == "permit" else False
    else:
        dec = True if st == "open" else False
    if not dec:
        unauthCGR.append(cgl1)
        if cgl2 is not None:
            dec = handleSP(dec, dcgl2, ppc, crs, st)
            if not dec:
                unauthCGR.append(cgl2)

    final_decision = "permit" if dec else "deny"
    return final_decision, unauthCGR

