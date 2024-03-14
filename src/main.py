from src.database_interactions.mongo_connection import get_mongo_client, get_database, get_collection, \
    get_data_from_collection
from src.unifying_model.mapper import map_data_unit


def main():
    client, message = get_mongo_client(ip='10.100.207.21')
    print(message)
    if client is None:
        return

    database = get_database(client, 'enron')
    collection = get_collection(database, 'messages')

    documents = get_data_from_collection(collection)
    print(documents)

    # Map each document using map_data_unit
    mapped_documents = []
    for document in documents:
        mapped_document = map_data_unit(document)
        mapped_documents.extend(mapped_document)

    print(mapped_documents)


if __name__ == '__main__':
    main()
