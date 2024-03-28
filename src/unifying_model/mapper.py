import hashlib
import uuid
from src.utils.util_functions import write_urp_to_file, clear_or_create_file


def generate_unique_id(*args):
    """
    Generates a unique ID based on a combination of provided arguments.
    This uses a hash of the document's _id, the field name, and a UUID to ensure uniqueness.

    :param args: Arguments to be combined into a unique ID.
    :return: A string representing the unique ID.
    """
    combined = "_".join(map(str, args))
    unique_suffix = uuid.uuid4().hex
    hash_object = hashlib.sha256((combined + "_" + unique_suffix).encode())
    return hash_object.hexdigest()


def duMapper(document_id, parent_path, obj, results, file_path):
    """
    Recursively maps an object (or part of it) to unifying resource properties.
    :param file_path:
    :param document_id: The ID of the document being processed.
    :param parent_path: List of parent IDs leading to this object.
    :param obj: The current object being mapped.
    :param results: Accumulator for collecting the mapping results.
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            component_id = generate_unique_id(document_id, k, *parent_path)
            new_path = parent_path + [component_id]

            urp = {
                "_id": component_id,
                "value": {
                    "path": [document_id] if not parent_path else [document_id] + parent_path,
                    "id": component_id,
                    "K": k,
                }
            }

            if isinstance(v, dict):
                results.append(urp)
                write_urp_to_file(urp, file_path)
                duMapper(document_id, new_path, v, results, file_path)
            else:
                urp['value']['V'] = v
                results.append(urp)
                write_urp_to_file(urp, file_path)
    else:
        print(f"Non-dictionary object encountered: {obj} at path {'->'.join(parent_path)}")
        pass


def m(document, file_path):
    """
    Entry point for mapping a document to unifying resource properties.
    :param document: The document to map.
    :param file_path: The path to the file where URPs should be written.
    :return: A list of mappings corresponding to the document's fields.
    """
    clear_or_create_file(file_path)
    results = []
    document_id = document.get("_id", "UnknownID")
    duMapper(document_id, [], document, results, file_path)
    return results

