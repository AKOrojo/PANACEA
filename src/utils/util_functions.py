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

    :param data_units: List of data units.
    """

    def detect_conflicts_in_du(du, parent_decision=None, level=0, path="Root"):
        """
        Recursively checks for varying access decisions within a du.
        """
        # Get the current access decision
        current_decision = du.get('access_decision')

        # If there's a parent decision, and it differs from the current, we have a potential conflict
        if parent_decision is not None and current_decision != parent_decision:
            print(f"Potential conflict detected at '{path}': {parent_decision} vs {current_decision}")

        # Recurse into nested structures
        for key, value in du.items():
            if isinstance(value, dict):
                new_path = f"{path} -> {key}"
                detect_conflicts_in_du(value, current_decision, level + 1, new_path)

    # Iterate through each data unit and check for conflicts
    for id, du in data_units.items():
        du_id = du.get('_id')
        print(f"Checking data unit with ID: {du_id}")
        detect_conflicts_in_du(du)
