from src.database_interactions.mongo_connection import get_mongo_client, get_database, get_collection, \
    get_data_from_collection, generate_node_id
from src.policy.specification import split_and_bind_policies_to_urp, assign_policies_randomly
from src.unifying_model.mapper import m
from src.utils.log_config import get_logger
from src.utils.util_functions import detect_and_print_conflicts, write_urp_to_file, clear_or_create_file, \
    write_security_urp_to_file, write_finalized_data_units_to_file
from src.view_generation.projector import apply_policies_to_du
from src.view_generation.remodeler import reduce_by_key, finalize, remodelerMap

logger = get_logger(__name__)


def main():
    ip = '10.100.207.21'
    port = 27017

    client, message = get_mongo_client(ip=ip, port=port)
    if client:
        node_id = generate_node_id(client, ip, port)
        logger.info(f"Node ID: {node_id}")
    else:
        logger.error(f"Failed to connect to MongoDB.")
        return

    database = get_database(client, 'enron')
    collection = get_collection(database, 'messages')
    documents = get_data_from_collection(collection)

    # Map documents to the unified model
    mapped_documents = []
    for document in documents:
        mapped_document = m(document, node_id)
        mapped_documents.extend(mapped_document)

    clear_or_create_file('unifying_model/urpS.log')

    for urp in mapped_documents:
        write_urp_to_file(urp, 'unifying_model/urpS.log')

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
    # security_urps = assign_policies_randomly(mapped_documents, "body", security_metadata_variations,
    #                                          policy_variations)

    clear_or_create_file('policy/security_urp.log')
    for security_urp in security_urps:
        write_security_urp_to_file(security_urp, 'policy/security_urp.log')

    grouped_urps = remodelerMap(security_urps)
    reduced_data_units = {key: reduce_by_key(urps, key) for key, urps in grouped_urps.items()}
    finalized_data_units = {key: finalize(du) for key, du in reduced_data_units.items()}

    clear_or_create_file('view_generation/finalized_data_units.log')
    for finalized_data_unit in finalized_data_units.items():
        write_finalized_data_units_to_file(finalized_data_unit, 'view_generation/finalized_data_units.log')

    # Simulation
    ppc = "most-specific-overrides"
    crs = "denials-take-precedence"
    st = "open"

    finalized_du_with_policies = apply_policies_to_du(finalized_data_units, ppc, crs, st)
    detect_and_print_conflicts(finalized_du_with_policies)

    r


if __name__ == '__main__':
    main()
