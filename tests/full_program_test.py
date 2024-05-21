from src.access_control_view.mapper import m
from src.access_control_view.projector import projector_m, projector_r, projector_f
from src.access_control_view.specification import random_policy

document = {
    "_id": "doc1",
    "key": "value",
    "nested": {"body": "value"}
}

# Map documents to the unified model
mapped_documents = []
mapped_document = m(document)
mapped_documents.extend(mapped_document)

for urp_id, urp in mapped_documents:
    random_policy(urp)

arc_variations = [
    {
        "subject": {
            "id": "user123",
            "attributes": {
                "department": "sales"
            }
        }
    }
]

# Assuming combining option is defined
co = 'all'
crs = "denials-take-precedence"
ppc = "most-specific-overrides"
st = "open"

for arc in arc_variations:
    sec_map_dus = projector_m(mapped_documents, arc, co, crs)
    sec_reduces_data_units = {key: projector_r(urps, key) for key, urps in sec_map_dus.items()}
    sec_finalized_data_units = {key: projector_f(du, arc, co, crs, ppc, st) for key, du in sec_reduces_data_units.items()}

    print(sec_finalized_data_units)

