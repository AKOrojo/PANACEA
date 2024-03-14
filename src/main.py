from src.database_interactions.mongo_connection import get_mongo_client, get_database, get_collection, \
    get_data_from_collection
from src.unifying_model.mapper import m


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


if __name__ == '__main__':
    main()
