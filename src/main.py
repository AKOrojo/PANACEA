from src.access_control_view.mongo_connection import get_mongo_client, get_database, get_collection, \
    get_data_from_collection
from src.access_control_view.specification import random_policy
from src.access_control_view.mapper import m
from src.utils.log_config import get_logger
from src.access_control_view.util_functions import detect_and_print_conflicts, write_urp_to_file, clear_or_create_file, \
    write_security_urp_to_file, write_finalized_data_units_to_file
# from src.view_generation.projector import apply_policies_to_du
# from src.view_generation.remodeler import reduce_by_key, finalize, remodelerMap

logger = get_logger(__name__)


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

    clear_or_create_file('logs/urpS.log')

    # Apply random policies and metadata to each URP
    for urp_id, urp in mapped_documents:
        write_urp_to_file(urp, 'logs/urpS.log')

    clear_or_create_file('logs/security_urp.log')

    # Apply random policies and metadata to each URP
    for urp_id, urp in mapped_documents:
        random_policy(urp)
        write_security_urp_to_file(urp, 'logs/security_urp.log')

    # grouped_urps = remodelerMap(mapped_documents)
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


if __name__ == '__main__':
    main()
