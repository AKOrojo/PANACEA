import time

from access_control_view.mongo_connection import get_mongo_client, get_database, get_collection
from src.utils.log_config import get_logger
from src.access_control_view.mapper import mapper_pipeline

logger = get_logger(__name__)


def main():
    client, message = get_mongo_client(ip='10.100.207.21')
    if client is None:
        return

    database = get_database(client, 'enron')
    collection = get_collection(database, 'messages')

    start_time = time.time()

    mapped_documents = collection.aggregate(mapper_pipeline)

    count = 0
    for doc in mapped_documents:
        print(doc)
        count += 1

    elapsed_time = (time.time() - start_time) * 1000

    print(f"Number of URPS: {count}")
    print(f"Elapsed time: {elapsed_time:.2f} ms")


if __name__ == "__main__":
    main()

    # clear_or_create_file('unifying_model/urpS.log')
    #
    # for urp in mapped_documents:
    #     write_urp_to_file(urp, 'unifying_model/urpS.log')
    #
    # security_metadata_variations = [
    #     [{"aip": ["research"]}],
    #     [{"aip": ["administration"]}],
    #     [{"aip": ["marketing"]}],
    #     [{"aip": ["finance"]}],
    #     [{"aip": ["engineering"]}],
    # ]
    #
    # policy_variations = [
    #     # Group 1 policies: Positive access for research
    #     [{"exp": "s.ap in meta.aip", "tp": "positive"}],
    #
    #     # Group 2 policies: Negative access for administration
    #     [{"exp": "s.ap not in meta.aip", "tp": "negative"}],
    #
    #     # Group 3 policies: Mixed, positive for marketing but with conditions
    #     [{"exp": "s.role == 'Manager' and s.ap in meta.aip", "tp": "positive"}],
    #
    #     # Group 4 policies: Positive access during specific times
    #     [{"exp": "s.ap in meta.aip and s.time == 'BusinessHours'", "tp": "positive"}],
    #
    #     # Group 5 policies: Negative for non-engineering roles
    #     [{"exp": "s.role != 'Engineer' and s.ap not in meta.aip", "tp": "negative"}],
    # ]
    #
    # split_count = 5
    # security_urps = split_and_bind_policies_to_urp(mapped_documents, "body", security_metadata_variations,
    #                                                policy_variations, split_count)
    #
    # # security_urps = assign_policies_randomly(mapped_documents, "body", security_metadata_variations,
    # #                                          policy_variations)
    #
    # clear_or_create_file('policy/security_urp.log')
    # for security_urp in security_urps:
    #     write_security_urp_to_file(security_urp, 'policy/security_urp.log')
    #
    # grouped_urps = remodelerMap(security_urps)
    # reduced_data_units = {key: reduce_by_key(urps, key) for key, urps in grouped_urps.items()}
    # finalized_data_units = {key: finalize(du) for key, du in reduced_data_units.items()}
    #
    # clear_or_create_file('view_generation/finalized_data_units.log')
    # for finalized_data_unit in finalized_data_units.items():
    #     write_finalized_data_units_to_file(finalized_data_unit, 'view_generation/finalized_data_units.log')
    #
    # # Simulation
    # ppc = "most-specific-overrides"
    # crs = "denials-take-precedence"
    # st = "open"
    #
    # finalized_du_with_policies = apply_policies_to_du(finalized_data_units, ppc, crs, st)
    # detect_and_print_conflicts(finalized_du_with_policies)
