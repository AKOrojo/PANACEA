import unittest
from src.view_generation.remodeler import remodelerMap, reduce_by_key, finalize
import unittest


class TestEmailProcessing(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.urps = [
            {'value': {'path': ['email1', 'headers', 'date'], 'K': 'date', 'V': '2021-01-01'}},
            {'value': {'path': ['email1', 'headers', 'from'], 'K': 'from', 'V': 'sender@example.com'}},
            {'value': {'path': ['email1', 'headers', 'to'], 'K': 'to', 'V': 'recipient@example.com'}},
            {'value': {'path': ['email1', 'headers', 'subject'], 'K': 'subject', 'V': 'Hello World'}},
            {'value': {'path': ['email1', 'body'], 'K': 'body', 'V': 'This is a test email body.'}}
        ]

    def test_map_function(self):
        """Test that URPs are correctly grouped by their data unit identifier."""
        grouped_urps = remodelerMap(self.urps)
        self.assertIn('email1', grouped_urps)
        self.assertEqual(len(grouped_urps['email1']), 5)

    def test_reduce_by_key_function(self):
        """Test that grouped URPs are correctly reduced to a structured data unit."""
        grouped_urps = remodelerMap(self.urps)
        reduced_data_unit = reduce_by_key(grouped_urps['email1'], 'email1')
        self.assertIn('headers', reduced_data_unit['email1'])  # Access the nested 'email1' key
        self.assertIn('body', reduced_data_unit['email1'])
        self.assertEqual(reduced_data_unit['email1']['body'], 'This is a test email body.')

    def test_finalize_function(self):
        """Test that the data unit is correctly finalized."""
        grouped_urps = remodelerMap(self.urps)
        reduced_data_unit = reduce_by_key(grouped_urps['email1'], 'email1')
        finalized_data_unit = finalize(reduced_data_unit)
        self.assertNotIn('tbs', finalized_data_unit)
        self.assertNotIn('tbp', finalized_data_unit)
        self.assertIn('headers', finalized_data_unit['email1'])
        self.assertIn('body', finalized_data_unit['email1'])


if __name__ == '__main__':
    unittest.main()
