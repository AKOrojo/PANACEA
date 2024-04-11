from src.database_interactions.mongo_connection import get_mongo_client, get_database, get_collection, \
    get_data_from_collection
from src.policy.specification import split_and_bind_policies_to_urp, assign_policies_randomly
from src.unifying_model.mapper import m
from src.utils.log_config import get_logger
from src.utils.util_functions import detect_and_print_conflicts, write_urp_to_file, clear_or_create_file, \
    write_security_urp_to_file, write_finalized_data_units_to_file, print_urp, print_sec_urp
from src.view_generation.projector import apply_policies_to_du, projector
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

# Simulation
ppc = "most-specific-overrides"
crs = "denials-take-precedence"
st = "open"
co = "all"
arc = {"s": {"ap": ["research"], "role": "Manager"}, "e": {"time": "BusinessHours"}}
finalized_du_with_policies = projector(security_urps, co, crs, arc)
