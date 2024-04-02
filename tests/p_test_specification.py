import unittest
import random
from src.policy.specification import split_and_bind_policies_to_urp, assign_policies_randomly


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


class TestAssignPoliciesRandomly(unittest.TestCase):
    def setUp(self):
        random.seed(42)
        self.mapping_results = [
            {'value': {'path': ['doc1'], 'K': 'key1', 'V': 'value1'}},
            {'value': {'path': ['doc2'], 'K': 'key2', 'V': 'value2'}},
            {'value': {'path': ['doc3'], 'K': 'key3', 'V': 'value3'}}
        ]
        self.field_names = ['key1', 'key3']
        self.security_metadata_variations = [{'meta1': 'data1'}, {'meta2': 'data2'}]
        self.policy_variations = [[{'policy1': 'rule1'}], [{'policy2': 'rule2'}]]

    def test_random_policy_assignment(self):
        """Ensure random policies are assigned and entries not in field_names are unchanged."""
        result = assign_policies_randomly(self.mapping_results, self.field_names,
                                          self.security_metadata_variations, self.policy_variations)
        # Check for assigned 'meta' and 'pol' in matching entries
        for entry in result:
            if entry['value']['K'] in self.field_names:
                self.assertIn('meta', entry['value'])
                self.assertIn('pol', entry['value'])
            else:
                # Entries not matching field_names should remain unchanged
                self.assertNotIn('meta', entry['value'])
                self.assertNotIn('pol', entry['value'])

    def test_variability_of_assignment_over_multiple_runs(self):
        """Test that over multiple runs, we see a variety of assignments, indicating randomness."""
        variations_seen = set()
        num_runs = 10
        for _ in range(num_runs):
            result = assign_policies_randomly(self.mapping_results.copy(), self.field_names,
                                              self.security_metadata_variations, self.policy_variations)
            for entry in result:
                if entry['value']['K'] in self.field_names:
                    meta_id = tuple(entry['value'].get('meta').items())
                    pol_id = tuple(entry['value'].get('pol'))
                    meta_pol_id = (meta_id, pol_id)
                    variations_seen.add(meta_pol_id)

        # Check if we have seen more than one unique combination of meta and pol, indicating randomness
        self.assertTrue(len(variations_seen) > 1,
                        "Did not observe variability in policy and metadata assignments over multiple runs.")


if __name__ == '__main__':
    unittest.main()
