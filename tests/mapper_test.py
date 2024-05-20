import unittest
from src.access_control_view.mapper import duMapper, m


class TestMapper(unittest.TestCase):

    def test_duMapper_simple(self):
        # Test mapping a simple object
        results = duMapper(["doc1"], {"key": "value"})
        self.assertEqual(len(results), 1, "Should map one key-value pair")
        self.assertEqual(results[0]["K"], "key", "Key should be mapped correctly")
        self.assertEqual(results[0]["V"], "value", "Value should be mapped correctly")

    def test_duMapper_nested(self):
        # Test mapping a nested object
        results = duMapper(["doc1"], {"parent": {"child": "value"}})
        self.assertEqual(len(results), 2,
                         "Should map two URPs: one for the 'parent' key and one for the nested 'child' key")
        parent_urps = [urp for urp in results if urp["K"] == "parent"]
        self.assertEqual(len(parent_urps), 1, "The 'parent' key should be mapped to one URP")
        child_urps = [urp for urp in results if urp["K"] == "child"]
        self.assertEqual(len(child_urps), 1, "The 'child' key should be mapped to one URP")
        self.assertEqual(child_urps[0]["V"], "value", "Nested 'child' value should be 'value'")

    def test_m_function(self):
        # Test the m function with a simple document
        document = {
            "_id": "doc1",
            "key": "value",
            "nested": {"child": "value"}
        }
        mapped_documents = m(document)
        self.assertEqual(len(mapped_documents), 4,
                         "m function should map three key-value pairs, including the document's _id")
        keys_mapped = [doc[1]["K"] for doc in mapped_documents]
        self.assertIn("child", keys_mapped, "Child key should be mapped separately without nested notation")

    def test_longest_path_three_ids(self):
        document = {
            "_id": "doc1",
            "level1": {
                "level2": {
                    "level3": "value"
                }
            }
        }
        mapped_document = m(document)
        results = [urp[1] for urp in mapped_document]
        longest_path_length = max(len(result['path']) for result in results)
        self.assertEqual(longest_path_length, 3, "The longest path should contain 3 IDs")


if __name__ == '__main__':
    unittest.main()
