import random
from src.access_control_view.util_functions import setField


def random_policies_and_meta():
    """Generates random policies and metadata."""
    purposes = ["research", "administration", "marketing", "sales", "development", "testing", "customer support"]
    policies = []
    meta = {"aip": [], "pip": []}
    used_purposes = set()
    has_policy = random.random() < 0.5  # 50% probability to have at least one policy

    if has_policy:
        num_policies = random.randint(1, 3)  # From 1 to 3 policies
        for _ in range(num_policies):
            is_positive = random.random() < 0.5
            purpose = random.choice(purposes)
            while purpose in used_purposes:
                purpose = random.choice(purposes)
            used_purposes.add(purpose)

            if is_positive:
                meta["aip"].append(purpose)
            else:
                meta["pip"].append(purpose)

    if meta["aip"]:
        policies.append({
            "exp": "s.ap in meta.aip",
            "tp": "positive"
        })
    if meta["pip"]:
        policies.append({
            "exp": "s.ap in meta.pip",
            "tp": "negative"
        })

    return {"policies": policies, "meta": meta}


def random_policy(urp):
    # Generate random policies and metadata
    policies_and_meta = random_policies_and_meta()
    setField(urp, "meta", policies_and_meta["meta"])
    setField(urp, "pol", policies_and_meta["policies"])
