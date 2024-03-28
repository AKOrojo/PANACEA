import unittest

from src.policy.specification import split_and_bind_policies_to_urp


class TestSplitAndBindPoliciesToURP(unittest.TestCase):
    def test_single_field_name(self):
        """Test with a single field name."""
        mapping_results = [
            {'value': {'path': ['doc1'], 'K': 'key1', 'V': 'value1'}},
            {'value': {'path': ['doc1'], 'K': 'key2', 'V': 'value2'}},
            {'value': {'path': ['doc2'], 'K': 'key1', 'V': 'value3'}}
        ]
        field_names = 'key1'
        security_metadata_variations = [{'meta1': 'data1'}, {'meta2': 'data2'}]
        policy_variations = [[{'policy1': 'rule1'}], [{'policy2': 'rule2'}]]
        split_count = 2

        expected_result = [
            {'value': {'path': ['doc1'], 'K': 'key1', 'V': 'value1', 'meta': {'meta1': 'data1'},
                       'pol': [{'policy1': 'rule1'}]}},
            {'value': {'path': ['doc1'], 'K': 'key2', 'V': 'value2'}},
            {'value': {'path': ['doc2'], 'K': 'key1', 'V': 'value3', 'meta': {'meta2': 'data2'},
                       'pol': [{'policy2': 'rule2'}]}}
        ]

        result = split_and_bind_policies_to_urp(mapping_results, field_names, security_metadata_variations,
                                                policy_variations, split_count)
        self.assertEqual(result, expected_result)

    def test_multiple_field_names(self):
        """Test with multiple field names."""
        mapping_results = [
            {'value': {'path': ['doc1'], 'K': 'key1', 'V': 'value1'}},
            {'value': {'path': ['doc1'], 'K': 'key2', 'V': 'value2'}},
            {'value': {'path': ['doc2'], 'K': 'key1', 'V': 'value3'}},
            {'value': {'path': ['doc2'], 'K': 'key2', 'V': 'value4'}}
        ]
        field_names = ['key1', 'key2']
        security_metadata_variations = [{'meta': 'data1'}, {'meta': 'data2'}]
        policy_variations = [[{'policy': 'rule1'}], [{'policy': 'rule2'}]]
        split_count = 2

        expected_result = [
            {'value': {'path': ['doc1'], 'K': 'key1', 'V': 'value1', 'meta': {'meta': 'data1'},
                       'pol': [{'policy': 'rule1'}]}},
            {'value': {'path': ['doc1'], 'K': 'key2', 'V': 'value2', 'meta': {'meta': 'data1'},
                       'pol': [{'policy': 'rule1'}]}},
            {'value': {'path': ['doc2'], 'K': 'key1', 'V': 'value3', 'meta': {'meta': 'data2'},
                       'pol': [{'policy': 'rule2'}]}},
            {'value': {'path': ['doc2'], 'K': 'key2', 'V': 'value4', 'meta': {'meta': 'data2'},
                       'pol': [{'policy': 'rule2'}]}}
        ]

        result = split_and_bind_policies_to_urp(mapping_results, field_names, security_metadata_variations,
                                                policy_variations, split_count)
        self.assertEqual(result, expected_result)

    def test_entries_from_same_tree_grouped_together(self):
        """Ensure entries from the same tree are assigned to the same group."""
        mapping_results = [
            {'value': {'path': ['doc1'], 'K': 'key1', 'V': 'value1'}},
            {'value': {'path': ['doc1'], 'K': 'key2', 'V': 'value2'}},
            {'value': {'path': ['doc2'], 'K': 'key1', 'V': 'value3'}}
        ]
        field_names = ['key1', 'key2']
        security_metadata_variations = [{'meta': 'data'}] * 2
        policy_variations = [[{'policy': 'rule'}]] * 2
        split_count = 2

        # Apply the function
        result = split_and_bind_policies_to_urp(mapping_results, field_names, security_metadata_variations,
                                                policy_variations, split_count)
        print(result)

        doc1_meta_policies = [(entry['value'].get('meta'), entry['value'].get('pol')) for entry in result if
                              entry['value']['path'] == ['doc1']]
        self.assertTrue(all(x == doc1_meta_policies[0] for x in doc1_meta_policies),
                        "Entries from the same tree do not have the same policies and metadata.")

    def test_all_elements_split_across_groups(self):
        """Test that all elements are evenly split across the specified number of groups."""
        mapping_results = [{'value': {'path': ['doc'], 'K': f'key{i}', 'V': f'value{i}'}} for i in range(10)]
        field_names = [f'key{i}' for i in range(10)]
        security_metadata_variations = [{'meta': f'data{i}'} for i in range(5)]
        policy_variations = [[{'policy': f'rule{i}'}] for i in range(5)]
        split_count = 5

        result = split_and_bind_policies_to_urp(mapping_results, field_names, security_metadata_variations,
                                                policy_variations, split_count)

        meta_policy_group_indices = []
        for entry in result:
            if 'meta' in entry['value']:
                meta = entry['value']['meta']
                index = security_metadata_variations.index(meta)
                meta_policy_group_indices.append(index)

        group_distribution = {index: meta_policy_group_indices.count(index) for index in set(meta_policy_group_indices)}
        expected_distribution = len(mapping_results) // split_count

        for group_index, count in group_distribution.items():
            self.assertEqual(count, expected_distribution,
                             f"Group {group_index} does not have the expected number of elements.")


if __name__ == '__main__':
    unittest.main()
