from src.access_control_view.util_functions import setField
import uuid


def anonymize(value):
    """
    Anonymizes a given value based on its type.

    :param value: The value to be anonymized.
    :return: The anonymized value.
    """
    if isinstance(value, str):
        return "[Anonymized String]"
    elif isinstance(value, int):
        return -1
    elif isinstance(value, float):
        return -1.0
    elif isinstance(value, bool):
        return False
    elif isinstance(value, list):
        return ["[Anonymized List]"]
    elif isinstance(value, dict):
        return {"[Anonymized Dict]": None}
    else:
        return None


def generateId():
    """Generates a unique identifier for each URP. For simplicity, use UUID."""
    return str(uuid.uuid4())


def push(list_obj, element):
    """Appends an element to a list."""
    list_obj.append(element)


def duMapper(cPath, obj):
    """
    Recursively analyzes components of a data unit 'obj', generating URPs.

    :param cPath: The current path to the component being analyzed.
    :param obj: The current object or component of the data unit being analyzed.
    :return: A set (list for simplicity) of objects modeling URPs.
    """
    urpS = []
    for f, v in obj.items():
        urp = {}
        setField(urp, "path", cPath.copy())
        setField(urp, "id", generateId())
        setField(urp, "K", f)
        if isinstance(v, dict):
            sPath = cPath.copy()
            push(sPath, urp["id"])
            sUrpS = duMapper(sPath, v)
            urpS.extend(sUrpS)
        else:
            anonymized_v = anonymize(v)  # Anonymize the simple field value
            setField(urp, "V", anonymized_v)
        push(urpS, urp)
    return urpS


def m(du, node_id):
    """The mapping function 'm' that processes a data unit 'du'."""
    emitted_pairs = []
    urpS = duMapper([node_id, du.get('_id')], du)
    for urp in urpS:
        emitted_pairs.append((urp['id'], urp))
    return emitted_pairs
