import unittest
import nlp_utils

class TestNlpUtils(unittest.TestCase):
    def test__get_source(self):
        nlp_tools = nlp_utils.NlpUtils()
        nbow = nlp_tools.get_normalized_bag_of_words('and apples', scale_by_idf=False)
        self.assertEqual(nbow['and'], nbow['apples'])
        nbow_scaled_by_idf = nlp_tools.get_normalized_bag_of_words('and apples', scale_by_idf=True)
        self.assertLess(nbow_scaled_by_idf['and'], nbow_scaled_by_idf['apples'])

if __name__ == "__main__":
    unittest.main()
    
