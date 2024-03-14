from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from src.utils.log_config import get_logger

logger = get_logger(__name__)


def get_mongo_client(ip='localhost', port=27017):
    """
    Attempts to connect to a MongoDB server and returns a status message.

    :param ip: The IP address of the MongoDB server. Defaults to 'localhost'.
    :param port: The port on which the MongoDB server is running. Defaults to 27017.
    :return: Tuple containing a MongoClient object or None, and a status message.
    """
    try:
        client = MongoClient(ip, port)
        logger.info("MongoDB connection successful.")
        return client, "MongoDB connection successful."
    except ConnectionFailure as e:
        logger.error(f"MongoDB connection failed: {e}")
        return None, f"MongoDB connection failed: {e}"
    except Exception as e:
        logger.error(f"An error occurred: {e}")
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


def get_data_from_collection(collection, query={}):
    """
    Retrieves data from a specified collection using a query.

    :param collection: The collection object from which to retrieve the data.
    :param query: A dictionary specifying the query conditions. Defaults to an empty dict, which retrieves all documents.
    :return: A list of documents matching the query.
    """
    try:
        documents = list(collection.find(query))
        logger.info(f"Retrieved {len(documents)} documents from collection '{collection.name}'.")
        return documents
    except Exception as e:
        logger.error(f"Failed to retrieve data from collection '{collection.name}': {e}")
        return []
