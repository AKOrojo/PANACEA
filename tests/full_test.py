from src.policy.specification import split_and_bind_policies_to_urp
from src.unifying_model.mapper import m
from src.view_generation.projector import projector, evaluate, combinePs
from src.view_generation.remodeler import r, f, remodelerMap

document = {
    "_id": "doc1",
    "key": "value",
    "nested": {"body": "value"}
}

# Map documents to the unified model
mapped_documents = []
mapped_document = m(document)
mapped_documents.extend(mapped_document)

security_metadata_variations = [
    [{"aip": ["research"]}],
    [{"aip": ["administration"]}],
    [{"aip": ["marketing"]}],
    [{"aip": ["finance"]}],
    [{"aip": ["engineering"]}],
]

policy_variations = [
    # Group 1 policies: Positive access for research
    [{"exp": "s.ap in meta.aip", "tp": "positive"}],
    # Group 2 policies: Negative access for administration
    [{"exp": "s.ap not in meta.aip", "tp": "negative"}],
    # Group 3 policies: Mixed, positive for marketing but with conditions
    [{"exp": "s.role == 'Manager' and s.ap in meta.aip", "tp": "positive"}],
    # Group 4 policies: Positive access during specific times
    [{"exp": "s.ap in meta.aip and s.time == 'BusinessHours'", "tp": "positive"}],
    # Group 5 policies: Negative for non-engineering roles
    [{"exp": "s.role != 'Engineer' and s.ap not in meta.aip", "tp": "negative"}],
]

split_count = 5
security_urps = split_and_bind_policies_to_urp(mapped_documents, "body", security_metadata_variations, policy_variations, split_count)


grouped_urps = remodelerMap(security_urps)
reduced_data_units = {key: r(urps, key) for key, urps in grouped_urps.items()}
finalized_data_units = {key: f(du) for key, du in reduced_data_units.items()}

arc_variations = [
    {
        'subject': {'ap': 'research'},
        'policies': [
            {"exp": "s.ap in meta.aip", "tp": "positive"},
            {"exp": "s.ap not in meta.aip", "tp": "negative"}
        ]
    }
]

# arc_variations = [
#     {
#         'subject': {'ap': 'research'},
#         'policies': [
#             {"exp": "s.ap in meta.aip", "tp": "positive"},
#             {"exp": "s.ap not in meta.aip", "tp": "negative"}
#         ]
#     },
#     {
#         'subject': {'ap': 'administration'},
#         'policies': [
#             {"exp": "s.ap in meta.aip", "tp": "positive"},
#             {"exp": "s.ap not in meta.aip", "tp": "negative"}
#         ]
#     },
#     {
#         'subject': {'ap': 'marketing', 'role': 'Manager'},
#         'policies': [
#             {"exp": "s.role == 'Manager' and s.ap in meta.aip", "tp": "positive"},
#             {"exp": "s.ap not in meta.aip", "tp": "negative"}
#         ]
#     },
#     {
#         'subject': {'ap': 'finance', 'time': 'BusinessHours'},
#         'policies': [
#             {"exp": "s.ap in meta.aip and s.time == 'BusinessHours'", "tp": "positive"},
#             {"exp": "s.ap not in meta.aip", "tp": "negative"}
#         ]
#     },
#     {
#         'subject': {'ap': 'engineering', 'role': 'Analyst'},
#         'policies': [
#             {"exp": "s.ap in meta.aip", "tp": "positive"},
#             {"exp": "s.role != 'Engineer' and s.ap not in meta.aip", "tp": "negative"}
#         ]
#     }
# ]

# Assuming combining option is defined

combining_option = 'any'  # or 'all' based on your requirement

for arc in arc_variations:
    for key, urp_group in grouped_urps.items():
        # Process each URP in the group
        for urp in urp_group:
            # Evaluate access decisions for this URP
            access_decision = evaluate(urp, arc)
            urp['access_decision'] = access_decision

        # After evaluating all URPs in the group, combine decisions
        decisions_list = [list(urp['access_decision'].values()) for urp in urp_group]
        combined_decisions = [combinePs(decisions, combining_option) for decisions in decisions_list]

        # Assign combined decision back to each URP
        for urp, combined_decision in zip(urp_group, combined_decisions):
            urp['combined_decision'] = combined_decision
            print(urp)
            #print(f"URP ID {urp['id']} Combined Decision: {combined_decision}")

# Simulation
ppc = "most-specific-overrides"
crs = "denials-take-precedence"
st = "open"
co = "all"
arc = {"s": {"ap": ["research"], "role": "Manager"}, "e": {"time": "BusinessHours"}}
finalized_du_with_policies = projector(security_urps, co, crs, arc)
