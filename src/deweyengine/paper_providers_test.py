import unittest
import paper_providers

class TestPaperProviders(unittest.TestCase):
    def test__get_source(self):
        src = paper_providers._get_html('https://www.journals.uchicago.edu/toc/et/2020/130/4')
        self.assertIn('/doi/abs/10.1086/708011', src)
        self.assertIn('/doi/abs/10.1086/708534', src)
        self.assertIn('/doi/abs/10.1086/708535', src)
        self.assertIn('/doi/abs/10.1086/708536', src)
        self.assertIn('/doi/abs/10.1086/708179', src)

        src = paper_providers._get_html('https://www.journals.uchicago.edu/doi/full/10.1086/708534')
        self.assertIn('Aggregation, Risk, and Reductio', src)

if __name__ == "__main__":
    unittest.main()
    
