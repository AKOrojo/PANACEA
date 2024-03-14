from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


def get_mongo_client(ip='localhost', port=27017):
    """
    Attempts to connect to a MongoDB server and returns a status message.

    :param ip: The IP address of the MongoDB server. Defaults to 'localhost'.
    :param port: The port on which the MongoDB server is running. Defaults to 27017.
    :return: Tuple containing a MongoClient object or None, and a status message.
    """
    try:
        client = MongoClient(ip, port)
        return client, "MongoDB connection successful."
    except ConnectionFailure as e:
        return None, f"MongoDB connection failed: {e}"
    except Exception as e:
        return None, f"An error occurred: {e}"


def get_database(client, database_name):
    """
    Fetches and returns a reference to a database.

    :param client: MongoClient object.
    :param database_name: The name of the database to fetch.
    :return: Database object
    """
    return client[database_name]


def get_collection(database, collection_name):
    """
    Fetches and returns a reference to a collection within a database.

    :param database: Database object.
    :param collection_name: The name of the collection to fetch.
    :return: Collection object
    """
    return database[collection_name]


def get_collections(database):
    """
    Fetches and returns a list of collection names within a database.

    :param database: Database object.
    :return: List of collection names
    """
    return database.list_collection_names()
