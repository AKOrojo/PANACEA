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
