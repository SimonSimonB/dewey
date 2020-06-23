import numpy
import tqdm
import os
import math
import time
from pathlib import Path
from collections import defaultdict
import paper_store
import paper_providers
import similarity_measures

class SimilarPapersService:

    def __init__(self):
        store = paper_store.PaperStore('./dewey/db/papers.db')
        self._documents = store.get_all()
        self._similarity_measure = similarity_measures.TfIdfSimilarityCorpus(corpus=self._documents)

    def get_papers_by_similarity(self, query: str):
        #document_store = DocumentStore(SERIALIZATION_PATH)
        #document_store.expand_store("C:/Users/simon/Google Drive/Studium/Topics/Political Philosophy", 180)
        #document_store.expand_store("C:/Users/simon/Google Drive/Studium/Topics/Metaphysics", 10)
        #document_store.expand_store_from_philarchive()
        #print('Word that sums up the inputted text best\n: {}'.format(model.similar_by_vector(sum_embeddings)))

        print('Computing similarities...')
        papers_with_similarity = self._similarity_measure.get_similarities(query)
        print('Done.')

        return papers_with_similarity
        #for doi, similarity in sorted_by_similarity:
        #    print(similarity, next(paper['title'] for paper in documents if paper['doi'] == doi))

        #documents_with_similarity = [] 
        #for document in tqdm.tqdm(documents):
        #    print(document['title'])
        #    documents_with_similarity.append(
        #        (similarity_measure.get_similarity(inputted_text, document), document['title'])
        #    )

        #sorted_by_similarity = sorted(documents_with_similarity, key = lambda x: -x[0])
        #for similarity, document_name in sorted_by_similarity:
        #    print(similarity, document_name)


def _get_inputted_text():
    return 'This paper investigates the epistemic powers of democratic institutions through an \
        assessment of three epistemic models of democracy: the Condorcet Jury Theorem, \
        the Diversity Trumps Ability Theorem, and Dewey’s experimentalist model. Dewey’s \
        model is superior to the others in its ability to model the epistemic functions of \
        three constitutive features of democracy: the epistemic diversity of participants, the \
        interaction of voting with discussion, and feedback mechanisms such as periodic \
        elections and protests. It views democracy as an institution for pooling widely \
        distributed information about problems and policies of public interest by engaging the \
        participation of epistemically diverse knowers. Democratic norms of free discourse, \
        dissent, feedback, and accountability function to ensure collective, experimentallybased learning from the diverse experiences of different knowers. I illustrate these\
        points with a case study of community forestry groups in South Asia, whose epistemic\
        powers have been hobbled by their suppression of women’s participation'


if __name__ == '__main__':
    paper_db = paper_store.PaperStore('./dewey/db/papers.db')
    #SimilarPapersService().get_papers_by_similarity(_get_inputted_text())

    #for paper in paper_store.get_all():
    #    print(paper['doi'], len(paper['body']))
    #    if(len(paper['body']) < 100):
    #        print(f'Paper store size: {len(paper_store.get_all())}')
    #        paper_store.delete(paper['doi'])
    #        print(f'Paper store size: {len(paper_store.get_all())}')

    # PPA: stopped at 1995
    #paper_store = paper_store.PaperStore('./db/papers.db')
    dois_in_db = [paper['doi'] for paper in paper_db.get_all()]
    for paper in paper_providers.ethics_papers(exclude_dois=dois_in_db):
        print(f'{len(paper_db.get_all())} currently in the store.')
        paper_db.insert(paper)