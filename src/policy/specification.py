def split_and_bind_policies_to_urp(mapping_results, field_name, security_metadata_variations, policy_variations,
                                   split_count):
    """
    Splits URPs into specified groups and binds varying security metadata and policies to each group.

    :param mapping_results: The list of mappings produced by the m function.
    :param field_name: The name of the field to which the security metadata and policies should be applied.
    :param security_metadata_variations: A list of dictionaries, each containing security metadata for a group.
    :param policy_variations: A list of lists of dictionaries, each representing the policies to be applied to a group.
    :param split_count: The number of groups to split the URPs into.
    :return: None; the function updates the mapping_results in place.
    """
    # Filter URPs by field name
    relevant_urps = [entry for entry in mapping_results if entry['value'].get('K') == field_name]

    urps_per_group = max(1, len(relevant_urps) // split_count)

    for i, entry in enumerate(relevant_urps):
        group_index = i // urps_per_group
        group_index = min(group_index, len(security_metadata_variations) - 1, len(policy_variations) - 1)

        # Assign security metadata and policies based on group
        entry['value']['meta'] = security_metadata_variations[group_index]
        entry['value']['pol'] = policy_variations[group_index]


