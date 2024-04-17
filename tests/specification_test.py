import unittest

from src.policy.specification import split_and_bind_policies_to_urp


class TestSplitAndBindPoliciesToURP(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures with the correct URP format."""
        self.urps = [
            ('d1e7d0ab-10aa-4f0f-ba84-4fd398fa0f9f',
             {'path': ['email1'], 'id': 'd1e7d0ab-10aa-4f0f-ba84-4fd398fa0f9f', 'K': '_id', 'V': 'email1'}),
            ('daf71e95-812b-41bc-a8be-6521d92e1584',
             {'path': ['email1'], 'id': 'daf71e95-812b-41bc-a8be-6521d92e1584', 'K': 'header_id', 'V': 'H123456'}),
            ('346b5007-f3bc-4f9b-9a8f-8a3c00f30196',
             {'path': ['email1', 'headers'], 'id': '346b5007-f3bc-4f9b-9a8f-8a3c00f30196', 'K': 'date',
              'V': '2021-01-01'}),
            ('4ad81f3c-e742-4464-b499-eb4f8b288903',
             {'path': ['email1', 'headers'], 'id': '4ad81f3c-e742-4464-b499-eb4f8b288903', 'K': 'from',
              'V': 'sender@example.com'}),
            ('f390047b-419c-4b11-9a77-0286248b11e7',
             {'path': ['email1', 'headers'], 'id': 'f390047b-419c-4b11-9a77-0286248b11e7', 'K': 'to',
              'V': 'recipient@example.com'}),
            ('d2758d0c-2638-41c5-af40-e0ceb8e61b27',
             {'path': ['email1', 'headers'], 'id': 'd2758d0c-2638-41c5-af40-e0ceb8e61b27', 'K': 'subject',
              'V': 'Hello World'}),
            ('823237be-724e-4037-9914-aadaa7c112ef',
             {'path': ['email1'], 'id': '823237be-724e-4037-9914-aadaa7c112ef', 'K': 'body',
              'V': 'This is a test email body.'})
        ]
        self.field_names = ['_id', 'date', 'from', 'to', 'subject', 'body']
        self.security_metadata_variations = [{'meta': 'data1'}, {'meta': 'data2'}]
        self.policy_variations = [[{'policy': 'rule1'}], [{'policy': 'rule2'}]]
        self.split_count = 2

    def test_single_field_name(self):
        """Test binding to a single specified field."""
        field_names = ['_id']
        result = split_and_bind_policies_to_urp(self.urps, field_names, self.security_metadata_variations,
                                                self.policy_variations, self.split_count)
        for urp in result:
            if urp[1]['K'] in field_names:
                self.assertIn('meta', urp[1])
                self.assertIn('pol', urp[1])

    def test_multiple_field_names(self):
        """Test binding to multiple specified fields."""
        field_names = ['date', 'from', 'to']
        result = split_and_bind_policies_to_urp(self.urps, field_names, self.security_metadata_variations,
                                                self.policy_variations, self.split_count)
        for urp in result:
            if urp[1]['K'] in field_names:
                self.assertIn('meta', urp[1])
                self.assertIn('pol', urp[1])

    def test_no_match_field(self):
        """Ensure fields not specified do not receive policies or metadata."""
        field_names = ['header_id']  # Assuming 'header_id' should not receive policies
        result = split_and_bind_policies_to_urp(self.urps, field_names, self.security_metadata_variations,
                                                self.policy_variations, self.split_count)
        for urp in result:
            if urp[1]['K'] not in field_names:
                self.assertNotIn('meta', urp[1])
                self.assertNotIn('pol', urp[1])


if __name__ == '__main__':
    unittest.main()
