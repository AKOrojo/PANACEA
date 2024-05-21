#from src.access_control_view.specification import split_and_bind_policies_to_urp
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
      'subject': {'aip': 'research'},
  }
]

# Assuming combining option is defined
co = 'all'
crs = "denials-take-precedence"
ppc = "most-specific-overrides"
st = "open"
#
for arc in arc_variations:
    sec_map_dus = projector_m(mapped_documents, arc, co, crs)
    sec_reduces_data_units = {key: projector_r(urps, key) for key, urps in sec_map_dus.items()}
    sec_finalized_data_units = {key: projector_f(du, arc, co, crs, ppc, st) for key, du in sec_reduces_data_units.items()}

    print(sec_finalized_data_units)

#
# reduce_derived_proj = [
#     ("3e29",
#      {"tbs": ["53da"],
#       "tbp": [],
#       "meta": [{"id": "body",
#                 "path": ["3e29"],
#                 "psSet": [{"aip": ["research, administration"],
#                            "pip": ["marketing"]}]}],
#       "pol": [{"id": "body",
#                "path": ["3e29"],
#                "psa": ["s.ap in meta.aip"],
#                "psp": ["s.ap in meta pip"]}],
#       "body": "I'm ready, are you?",
#       "headers": "53da",
#       "53da": {
#           "From": "daphneco64@bigplanet.com",
#       }})]
#
# x = {'doc1':
#      {'_id': 'doc1',
#       'key': 'value',
#       'f93ac727-941b-4ef5-8897-3166f9215832': {'body': 'value'},
#       'nested': 'f93ac727-941b-4ef5-8897-3166f9215832',
#       'tbs': ['f93ac727-941b-4ef5-8897-3166f9215832'],
#       'tbp': ['f93ac727-941b-4ef5-8897-3166f9215832'],
#       'meta': [{'id': '67adb03f-562a-45b5-8946-75690a5db8f6',
#                 'path': ['doc1', 'f93ac727-941b-4ef5-8897-3166f9215832'],
#                 'psSet': [{'aip': ['research']}, {'aip': ['marketing']}]}],
#       'pol': [{'id': '67adb03f-562a-45b5-8946-75690a5db8f6',
#                'path': ['doc1', 'f93ac727-941b-4ef5-8897-3166f9215832'],
#                'psa': ['s.ap in meta.aip'],
#                'psp': ['s.ap in meta.aip']}]}}
