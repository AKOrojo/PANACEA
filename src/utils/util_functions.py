from src.utils.log_config import get_logger
import json
from bson import ObjectId

logger = get_logger(__name__)


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)  # Convert ObjectId to string
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


def write_finalized_data_units_to_file(finalized_data_units, file_path):
    """
    Writes each finalized data unit to its own line in a file, handling special types like ObjectId.

    :param finalized_data_units: A dictionary containing all finalized data units.
    :param file_path: The path to the file where the finalized data units should be written.
    """
    with open(file_path, 'w') as f:
        for _, data_unit in finalized_data_units.items():
            # Serialize each data unit with custom handling for ObjectId
            serialized_data_unit = json.dumps(data_unit, cls=CustomEncoder)
            f.write(serialized_data_unit + '\n')  # Write each unit on its own line


def print_urp(urp):
    """
    Prints a Unifying Resource Property (URP) in a structured and readable format.

    :param urp: The URP dictionary to print.
    """

    if 'value' in urp:
        value_str = "{\n"
        value_str += f"  'path': {urp['value'].get('path', [])},\n"
        value_str += f"  'id': '{urp['value'].get('id', 'Unknown')}',\n"
        value_str += f"  'K': '{urp['value'].get('K', 'Unknown')}',\n"
        if 'V' in urp['value']:
            value_str += f"  'V': '{urp['value'].get('V', 'Unknown')}'\n"
        value_str += "}"
        print(f"{{'_id': '{urp.get('_id', 'Unknown')}',\n'value': {value_str}}}\n")
    else:
        # Fallback
        print(f"URP does not have the expected structure: {urp}")


def clear_or_create_file(file_path):
    """
    Clears the content of the given file or creates it if it doesn't exist.

    :param file_path: The path to the file to be cleared or created.
    """
    open(file_path, 'w').close()


def write_urp_to_file(urp, file_path):
    """
    Writes a Unifying Resource Property (URP) to a file in a structured and readable format.

    :param urp: The URP dictionary to write.
    :param file_path: The path to the file where the URP should be written.
    """
    with open(file_path, 'a') as file:  # Open the file in append mode
        if 'value' in urp:
            value_str = "{\n"
            value_str += f"  'path': {urp['value'].get('path', [])},\n"
            value_str += f"  'id': '{urp['value'].get('id', 'Unknown')}',\n"
            value_str += f"  'K': '{urp['value'].get('K', 'Unknown')}',\n"
            if 'V' in urp['value']:
                value_str += f"  'V': '{urp['value'].get('V', 'Unknown')}'\n"
            value_str += "}"
            file.write(f"{{'_id': '{urp.get('_id', 'Unknown')}',\n'value': {value_str}}}\n\n")
        else:
            # Fallback in case the URP does not have the expected structure
            file.write(f"URP does not have the expected structure: {urp}\n\n")


def write_security_urp_to_file(urp, file_path):
    """
    Writes a URP with its security metadata and policies to a file in a structured and readable format.

    :param urp: The URP dictionary to write, including its security metadata and policies.
    :param file_path: The path to the file where the URP should be written.
    """
    with open(file_path, 'a') as file:  # Open the file in append mode
        value_str = "{\n"
        value_str += f"  'path': {urp['value'].get('path', [])},\n"
        value_str += f"  'id': '{urp['value'].get('id', 'Unknown')}',\n"
        value_str += f"  'K': '{urp['value'].get('K', 'Unknown')}',\n"
        if 'V' in urp['value']:
            value_str += f"  'V': '{urp['value'].get('V', 'Unknown')}',\n"
        if 'meta' in urp['value']:
            value_str += f"  'meta': {urp['value'].get('meta', {})},\n"
        if 'pol' in urp['value']:
            value_str += f"  'pol': {urp['value'].get('pol', [])}\n"
        value_str += "}"
        file.write(f"{{'_id': '{urp.get('_id', 'Unknown')}',\n'value': {value_str}}}\n\n")


def detect_and_print_conflicts(data_units):
    """
    Detects potential conflicts within data units based on varying access decisions
    at different nested levels and prints details about these data units.

    :param data_units: Dictionary of data units.
    """

    def detect_conflicts_in_du(du, parent_decision=None, path="Root"):
        """
        Recursively checks for varying access decisions within a du, accommodating
        for direct access_decision entries as well as nested DU structures.
        """
        if isinstance(du, dict):
            current_decision = du.get('access_decision')
            if parent_decision and current_decision and parent_decision != current_decision:
                logger.info(
                    f"Conflict detected at '{path}': Parent decision '{parent_decision}' vs Current decision '{current_decision}'")
            for key, value in du.items():
                new_path = f"{path} -> {key}"
                detect_conflicts_in_du(value, current_decision, new_path)
        elif isinstance(du, str) and path.endswith('access_decision'):
            if parent_decision and parent_decision != du:
                logger.error(
                    f"Conflict detected at '{path}': Parent decision '{parent_decision}' vs Current decision '{du}'")
                print(f"Conflict detected at '{path}': Parent decision '{parent_decision}' vs Current decision '{du}'")

    for du_key, du_value in data_units.items():
        if isinstance(du_value, dict):
            logger.info(f"Checking data unit with key: {du_key}")
            detect_conflicts_in_du(du_value)
        else:
            logger.info(f"Non-standard entry found with key: {du_key}, value: {du_value} ({type(du_value).__name__})")
