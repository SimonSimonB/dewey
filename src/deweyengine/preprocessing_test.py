import unittest
import preprocessing

class TestPreprocessing(unittest.TestCase):
    def test(self):
        self.assertNotIn('that', preprocessing.remove_common_words('That house looks nice'))
        self.assertNotIn('That', preprocessing.remove_common_words('That house looks nice'))
        self.assertIn('house', preprocessing.remove_common_words('That house looks nice'))
    
    #def test_with_actual_paper(self):
    #    with open('./cached_papers/', 'r', encoding='utf-8') as f:




if __name__ == "__main__":
    unittest.main()
 