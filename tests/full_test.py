from src.policy.specification import split_and_bind_policies_to_urp
from src.unifying_model.mapper import m
from src.view_generation.projector import evaluate, combinePs, conflictRes, projector_r, projector_f, projector_m
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
    [{"aip": ["research"]}, {"aip": ["marketing"]}],
    [{"aip": ["administration"]}],
    [{"aip": ["marketing"]}],
    [{"aip": ["finance"]}],
    [{"aip": ["engineering"]}],
]

policy_variations = [
    # Group 1 policies: Positive access for research
    [{"exp": "s.ap in meta.aip", "tp": "positive"}, {"exp": "s.ap in meta.aip", "tp": "negative"}],
    # Group 2 policies: Negative access for administration
    [{"exp": "s.ap not in meta.aip", "tp": "negative"}],
]

split_count = 5
security_urps = split_and_bind_policies_to_urp(mapped_documents, "body", security_metadata_variations,
                                               policy_variations, split_count)

# grouped_urps = remodelerMap(security_urps)
# reduced_data_units = {key: r(urps, key) for key, urps in grouped_urps.items()}
# finalized_data_units = {key: f(du) for key, du in reduced_data_units.items()}

arc_variations = [
    {
        'subject': {'aip': 'research'},
    }
]

# Assuming combining option is defined
co = 'all'
crs = "denials-take-precedence"

for arc in arc_variations:
    sec_map_dus = projector_m(security_urps, arc, co, crs)
    for key, sec_map in sec_map_dus.items():
        for urp in sec_map:
            print(urp)


    sec_reduces_data_units = {key: projector_r(urps, key) for key, urps in sec_map_dus.items()}
    sec_finalized_data_units = {key: projector_f(du) for key, du in sec_reduces_data_units.items()}
#
    print(sec_finalized_data_units)
#
# # Simulation
# ppc = "most-specific-overrides"
#
# st = "open"
# co = "all"
# arc = {"s": {"ap": ["research"], "role": "Manager"}, "e": {"time": "BusinessHours"}}

