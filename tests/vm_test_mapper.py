import unittest
from src.view_generation.mapper import r, f


class TestMapperFunctions(unittest.TestCase):

    def test_r_and_f_integration(self):
        # Input data
        urpS = [{
            "id": "53d6",
            "value": {
                "path": ["53d3", "53d4", "3е29"],
                "id": "53d6",
                "K": "body",
                "V": "I'm ready, are you?....",
                "meta": [{"aip": ["research", "administration"]},
                         {"pip": ["marketing"]}],
                "pol": [{"exp": "s.ap in meta.aip", "tp": "positive"},
                        {"exp": "s.ap in meta.pip", "tp": "negative"}]
            }
        }]
        key = '3е29'

        # Expected outcome
        expected_du = {
            'body': "I'm ready, are you?...."
        }

        # Process the input data
        du = r(urpS, key)
        result_du = f(du)

        # Assert that the processed data matches the expected outcome
        self.assertEqual(result_du, expected_du)


if __name__ == '__main__':
    unittest.main()
