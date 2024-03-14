from src.database_interactions.mongo_connection import get_mongo_client, get_database, get_collection, get_data_from_collection


def main():
    client, message = get_mongo_client(ip='10.100.207.21')
    print(message)
    if client is None:
        return

    database = get_database(client, 'enron')
    collection = get_collection(database, 'messages')

    documents = get_data_from_collection(collection)
    print(documents)


if __name__ == '__main__':
    main()
