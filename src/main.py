from src.database_interactions.mongo_connection import get_mongo_client, get_database, get_collection, \
    get_data_from_collection
from src.policy.specification import split_and_bind_policies_to_urp
from src.unifying_model.mapper import m
from src.view_generation.projector import apply_policies_to_du
from src.view_generation.remodeler import reduce_by_key, finalize, remodelerMap


def main():
    client, message = get_mongo_client(ip='10.100.207.21')
    print(message)
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

    print(finalized_data_units)

    # Simulation
    ppc = "most-specific-overrides"
    crs = "denials-take-precedence"
    st = "open"

    finalized_du_with_policies = apply_policies_to_du(finalized_data_units, ppc, crs, st)
    print(finalized_du_with_policies)


if __name__ == '__main__':
    main()
