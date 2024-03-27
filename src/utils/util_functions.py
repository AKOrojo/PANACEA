from src.utils.log_config import get_logger

logger = get_logger(__name__)


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
                logger.info(f"Conflict detected at '{path}': Parent decision '{parent_decision}' vs Current decision '{current_decision}'")
            for key, value in du.items():
                new_path = f"{path} -> {key}"
                detect_conflicts_in_du(value, current_decision, new_path)
        elif isinstance(du, str) and path.endswith('access_decision'):
            if parent_decision and parent_decision != du:
                logger.error(f"Conflict detected at '{path}': Parent decision '{parent_decision}' vs Current decision '{du}'")
                print(f"Conflict detected at '{path}': Parent decision '{parent_decision}' vs Current decision '{du}'")

    for du_key, du_value in data_units.items():
        if isinstance(du_value, dict):
            logger.info(f"Checking data unit with key: {du_key}")
            detect_conflicts_in_du(du_value)
        else:
            logger.info(f"Non-standard entry found with key: {du_key}, value: {du_value} ({type(du_value).__name__})")
