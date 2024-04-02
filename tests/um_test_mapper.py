import unittest
from src.unifying_model.mapper import generate_unique_id, duMapper, m
from src.utils.util_functions import print_urp


class TestMapper(unittest.TestCase):

    def test_generate_unique_id(self):
        # Test uniqueness
        id1 = generate_unique_id("doc1", "field1")
        id2 = generate_unique_id("doc1", "field1")
        self.assertNotEqual(id1, id2, "Generated IDs should be unique")

        # Test reproducibility with UUID segment
        id3 = generate_unique_id("doc1", "field2")
        id4 = generate_unique_id("doc1", "field2")
        self.assertNotEqual(id3, id4, "Generated IDs for different fields should be unique")

    def test_duMapper_simple(self):
        # Test mapping a simple object
        results = []
        duMapper("doc1", [], {"key": "value"}, results)
        self.assertEqual(len(results), 1, "Should map one key-value pair")
        self.assertIn("key", results[0]["value"]["K"], "Key should be mapped correctly")
        self.assertIn("value", results[0]["value"]["V"], "Value should be mapped correctly")

    def test_duMapper_nested(self):
        # Test mapping a nested object
        results = []
        duMapper("doc1", [], {"parent": {"child": "value"}}, results)
        self.assertEqual(len(results), 2, "Should map two URPs: one for the 'parent' key and one for the nested "
                                          "'child' key")
        parent_urps = [urp for urp in results if urp["value"]["K"] == "parent"]
        self.assertEqual(len(parent_urps), 1, "The 'parent' key should be mapped to one URP")
        child_urps = [urp for urp in results if urp["value"]["K"] == "child"]
        self.assertEqual(len(child_urps), 1, "The 'child' key should be mapped to one URP within 'parent'")
        self.assertEqual(child_urps[0]["value"]["V"], "value", "Nested 'child' value should be 'value'")

    def test_m_function(self):
        # Test the m function with a simple document
        document = {
            "_id": "doc1",
            "key": "value",
            "nested": {"child": "value"}
        }
        mapped_documents = m(document)
        for urp in mapped_documents:
            print_urp(urp)
        self.assertEqual(len(mapped_documents), 4,
                         "m function should map three key-value pairs, including the document's _id")
        keys_mapped = [doc["value"]["K"] for doc in mapped_documents]
        self.assertIn("child", keys_mapped, "Child key should be mapped as separate without nested notation")

    def test_longest_path_three_ids(self):
        document = {
            "_id": "doc1",
            "level1": {
                "level2": {
                    "level3": "value"
                }
            }
        }
        results = []
        mapped_document = m(document)
        results.extend(mapped_document)

        for urp in results:
            print_urp(urp)

        longest_path_length = max(len(result['value']['path']) for result in results)
        self.assertEqual(longest_path_length, 3, "The longest path should contain 3 IDs")


if __name__ == '__main__':
    unittest.main()
