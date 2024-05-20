import unittest

from src.view_generation.remodeler import remodelerMap, r, f


class TestEmailProcessing(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.urps = [
            ('d1e7d0ab-10aa-4f0f-ba84-4fd398fa0f9f',
             {'path': ['email1'], 'id': 'd1e7d0ab-10aa-4f0f-ba84-4fd398fa0f9f', 'K': '_id', 'V': 'email1'}),
            ('daf71e95-812b-41bc-a8be-6521d92e1584',
             {'path': ['email1'], 'id': 'daf71e95-812b-41bc-a8be-6521d92e1584', 'K': 'header_id', 'V': 'H123456'}),
            ('346b5007-f3bc-4f9b-9a8f-8a3c00f30196',
             {'path': ['email1', 'bc58308a-5968-49a9-a5d4-90740efa8e40'], 'id': '346b5007-f3bc-4f9b-9a8f-8a3c00f30196',
              'K': 'date', 'V': '2021-01-01'}),
            ('4ad81f3c-e742-4464-b499-eb4f8b288903',
             {'path': ['email1', 'bc58308a-5968-49a9-a5d4-90740efa8e40'], 'id': '4ad81f3c-e742-4464-b499-eb4f8b288903',
              'K': 'from', 'V': 'sender@example.com'}),
            ('f390047b-419c-4b11-9a77-0286248b11e7',
             {'path': ['email1', 'bc58308a-5968-49a9-a5d4-90740efa8e40'], 'id': 'f390047b-419c-4b11-9a77-0286248b11e7',
              'K': 'to', 'V': 'recipient@example.com'}),
            ('d2758d0c-2638-41c5-af40-e0ceb8e61b27',
             {'path': ['email1', 'bc58308a-5968-49a9-a5d4-90740efa8e40'], 'id': 'd2758d0c-2638-41c5-af40-e0ceb8e61b27',
              'K': 'subject', 'V': 'Hello World'}),
            ('bc58308a-5968-49a9-a5d4-90740efa8e40',
             {'path': ['email1'], 'id': 'bc58308a-5968-49a9-a5d4-90740efa8e40', 'K': 'headers'}),
            ('823237be-724e-4037-9914-aadaa7c112ef',
             {'path': ['email1'], 'id': '823237be-724e-4037-9914-aadaa7c112ef', 'K': 'body',
              'V': 'This is a test email body.'})
        ]

    def test_map_function(self):
        """Test that URPs are correctly grouped by their data unit identifier."""
        grouped_urps = remodelerMap(self.urps)
        self.assertIn('email1', grouped_urps)
        self.assertEqual(len(grouped_urps['email1']), 8)

    def test_reduce_by_key_function(self):
        """Test that grouped URPs are correctly reduced to a structured data unit."""
        grouped_urps = remodelerMap(self.urps)
        reduced_data_unit = r(grouped_urps['email1'], 'email1')
        # Check for individual keys instead of a 'headers' group
        self.assertIn('header_id', reduced_data_unit)
        self.assertIn('_id', reduced_data_unit)
        self.assertIn('headers', reduced_data_unit)
        self.assertIn('body', reduced_data_unit)
        self.assertEqual(reduced_data_unit['body'], 'This is a test email body.')

    def test_finalize_function(self):
        """Test that the data unit is correctly finalized."""
        grouped_urps = remodelerMap(self.urps)
        reduced_data_unit = r(grouped_urps['email1'], 'email1')
        finalized_data_unit = f(reduced_data_unit)
        print(finalized_data_unit)
        self.assertNotIn('tbs', finalized_data_unit)  # Ensure temp fields are removed
        self.assertNotIn('tbp', finalized_data_unit)  # Ensure temp fields are removed
        # Check for individual keys instead of a 'headers' group
        self.assertIn('_id', finalized_data_unit)
        self.assertIn('header_id', finalized_data_unit)
        self.assertIn('headers', finalized_data_unit)
        self.assertIn('body', finalized_data_unit)


if __name__ == '__main__':
    unittest.main()
