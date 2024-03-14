from src.database_interactions.mongo_connection import get_mongo_client, get_database, get_collection


def main():
    # Attempt to connect to MongoDB with default IP and port
    client, message = get_mongo_client(ip='10.100.207.21')
    print(message)
    if client is None:
        return

    # Get a database
    database = get_database(client, 'enron')

    # Get a specific collection from the database
    collection = get_collection(database, 'messages')
    print(f"Working with collection: {collection.name}")


if __name__ == '__main__':
    main()
