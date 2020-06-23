import unittest
import paper_store

class TestPaperStore(unittest.TestCase):
    def test(self):
        store = paper_store.PaperStore(':memory:')

        new_paper_attributes = {attribute.name: ('test text' if attribute.type == 'text' else 42) for attribute in paper_store.paper_attributes}
        store.insert(new_paper_attributes)
        self.assertEqual(len(store.get_all()), 1)
        paper_from_store = store.get_all()[0]

        for attribute_name, attribute_value in new_paper_attributes.items():
            self.assertEqual(paper_from_store[attribute_name], attribute_value)




if __name__ == "__main__":
    unittest.main()
 