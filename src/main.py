import time
from src.access_control_view.mongo_connection import get_mongo_client, get_database, get_collection, \
    get_data_from_collection
from src.access_control_view.projector import projector_m, projector_f, projector_r
from src.access_control_view.specification import random_policy
from src.access_control_view.mapper import m
from src.utils.log_config import get_logger
from src.access_control_view.util_functions import write_urp_to_file, clear_or_create_file, \
    write_security_urp_to_file, write_finalized_data_units_to_file

logger = get_logger(__name__)

def print_time(message, start_time):
    end_time = time.time()
    print(f"{message}: {int((end_time - start_time) * 1000)} ms")
    return end_time

def main():
    start_time = time.time()
    client, message = get_mongo_client(ip='10.100.207.21')
    if client is None:
        return
    start_time = print_time("get_mongo_client", start_time)

    database = get_database(client, 'enron')
    start_time = print_time("get_database", start_time)

    collection = get_collection(database, 'messages')
    start_time = print_time("get_collection", start_time)

    documents = get_data_from_collection(collection)
    start_time = print_time("get_data_from_collection", start_time)

    # Map documents to the unified model
    mapped_documents = []
    for document in documents:
        mapped_document = m(document)
        mapped_documents.extend(mapped_document)
    start_time = print_time("mapping_documents", start_time)

    clear_or_create_file('logs/urpS.log')
    start_time = print_time("clear_or_create_file urpS.log", start_time)

    # Apply random policies and metadata to each URP
    for urp_id, urp in mapped_documents:
        write_urp_to_file(urp, 'logs/urpS.log')
    start_time = print_time("write_urp_to_file", start_time)

    clear_or_create_file('logs/security_urp.log')
    start_time = print_time("clear_or_create_file security_urp.log", start_time)

    # Apply random policies and metadata to each URP
    for urp_id, urp in mapped_documents:
        random_policy(urp)
        write_security_urp_to_file(urp, 'logs/security_urp.log')
    start_time = print_time("random_policy and write_security_urp_to_file", start_time)

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
        start_time = print_time("projector_m", start_time)

        sec_reduces_data_units = {key: projector_r(urps, key) for key, urps in sec_map_dus.items()}
        start_time = print_time("projector_r", start_time)

        sec_finalized_data_units = {key: projector_f(du, arc, co, crs, ppc, st) for key, du in sec_reduces_data_units.items()}
        start_time = print_time("projector_f", start_time)

        clear_or_create_file('view_generation/finalized_data_units.log')
        start_time = print_time("clear_or_create_file finalized_data_units.log", start_time)

        for finalized_data_unit in sec_finalized_data_units.items():
            write_finalized_data_units_to_file(finalized_data_unit, 'view_generation/finalized_data_units.log')
        start_time = print_time("write_finalized_data_units_to_file", start_time)

if __name__ == '__main__':
    main()
