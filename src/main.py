from src.database_interactions.mongo_connection import get_mongo_client, get_database, get_collection, \
    get_data_from_collection
from src.policy.specification import split_and_bind_policies_to_urp, split_and_bind_policies_with_conflicts
from src.unifying_model.mapper import m
from src.utils.util_functions import detect_and_print_conflicts
from src.view_generation.projector import apply_policies_to_du
from src.view_generation.remodeler import reduce_by_key, finalize, remodelerMap


def main():
    client, message = get_mongo_client(ip='10.100.207.21')
    if client is None:
        return

    database = get_database(client, 'enron')
    collection = get_collection(database, 'messages')
    documents = get_data_from_collection(collection)

    # Map documents to the unified model
    mapped_documents = []
    for document in documents:
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
    security_urps = split_and_bind_policies_to_urp(mapped_documents, "body", security_metadata_variations,
                                                   policy_variations, split_count)

    grouped_urps = remodelerMap(security_urps)
    reduced_data_units = {key: reduce_by_key(urps, key) for key, urps in grouped_urps.items()}
    finalized_data_units = {key: finalize(du) for key, du in reduced_data_units.items()}

    # Simulation
    ppc = "most-specific-overrides"
    crs = "denials-take-precedence"
    st = "open"

    finalized_du_with_policies = apply_policies_to_du(finalized_data_units, ppc, crs, st)
    detect_and_print_conflicts(finalized_du_with_policies)

    # # Security metadata variations (for demonstration, these remain the same across variations)
    # security_metadata_variations = [
    #     [{"aip": ["research"]}],
    #     [{"aip": ["administration"]}],
    #     [{"aip": ["marketing"]}],
    #     [{"aip": ["finance"]}],
    #     [{"aip": ["engineering"]}],
    # ]
    #
    # # Policy variations that permit access based on certain criteria
    # policy_variations = [
    #     [{"exp": "s.ap in meta.aip and s.role == 'Manager'", "tp": "positive"}],  # Permit for managers in research
    #     [{"exp": "s.ap in meta.aip and s.department == 'Admin'", "tp": "positive"}],
    #     # Permit for Admin department in administration
    #     [{"exp": "s.ap in meta.aip and s.time == 'BusinessHours'", "tp": "positive"}],
    #     # Permit during business hours for marketing
    #     [{"exp": "s.ap in meta.aip and s.level >= 5", "tp": "positive"}],  # Permit for level >= 5 in finance
    #     [{"exp": "s.ap in meta.aip and s.project == 'ProjectX'", "tp": "positive"}],
    #     # Permit for Project X in engineering
    # ]
    #
    # # Conflicting policy variations that deny access for the same criteria
    # conflict_variations = [
    #     [{"exp": "s.ap in meta.aip and s.role == 'Manager'", "tp": "negative"}],
    #     [{"exp": "s.ap in meta.aip and s.department == 'Admin'", "tp": "negative"}],
    #     [{"exp": "s.ap in meta.aip and s.time == 'BusinessHours'", "tp": "negative"}],
    #     [{"exp": "s.ap in meta.aip and s.level >= 5", "tp": "negative"}],
    #     [{"exp": "s.ap in meta.aip and s.project == 'ProjectX'", "tp": "negative"}],
    # ]
    #
    # # Specify the number of groups to split the URPs into (matching the number of variations)
    # split_count = 5
    #
    # # Bind the policies to the URPs, introducing potential conflicts
    # security_urps_with_conflicts = split_and_bind_policies_with_conflicts(
    #     mapped_documents,
    #     "body",
    #     security_metadata_variations,
    #     policy_variations,
    #     conflict_variations,
    #     split_count
    # )
    #
    # # Example output inspection
    # for urp in security_urps_with_conflicts:
    #     print(urp["value"])


if __name__ == '__main__':
    main()
