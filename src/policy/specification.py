def split_and_bind_policies_to_urp(mapping_results, field_name, security_metadata_variations, policy_variations,
                                   split_count):
    """
    Splits URPs into specified groups and binds varying security metadata and policies to each group. Returns the updated mappings.

    :param mapping_results: The list of mappings produced by the m function.
    :param field_name: The name of the field to which the security metadata and policies should be applied.
    :param security_metadata_variations: A list of dictionaries, each containing security metadata for a group.
    :param policy_variations: A list of lists of dictionaries, each representing the policies to be applied to a group.
    :param split_count: The number of groups to split the URPs into.
    :return: A list of updated mappings with the new security metadata and policies applied.
    """
    updated_mappings = []  # Initialize a list to store updated mappings
    # Filter URPs by field name
    relevant_urps = [entry for entry in mapping_results if entry['value'].get('K') == field_name]

    urps_per_group = max(1, len(relevant_urps) // split_count)

    for i, entry in enumerate(relevant_urps):
        group_index = i // urps_per_group
        group_index = min(group_index, len(security_metadata_variations) - 1, len(policy_variations) - 1)

        # Copy the entry to avoid modifying the original mapping_results
        updated_entry = entry.copy()
        # Assign security metadata and policies based on group
        updated_entry['value']['meta'] = security_metadata_variations[group_index]
        updated_entry['value']['pol'] = policy_variations[group_index]

        # Add the updated entry to the list of updated mappings
        updated_mappings.append(updated_entry)

    return updated_mappings
