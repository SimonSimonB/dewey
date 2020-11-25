import pathlib
import tqdm
import scipy.sparse.linalg
import sklearn
import typing
import os
import nlp_utils

BIG_MODEL = False
WORD2VEC_MODEL_PATH = pathlib.Path(
    os.path.join(os.path.dirname(__file__),
                 '../../../../models/english_words_by_frequency.txt'))


class TfIdfSimilarityCorpus():

    def __init__(self, corpus: typing.Iterable[dict]):
        self._corpus = list(corpus)
        self._nlp_utils = nlp_utils.NlpUtils()
        self._tfidf_vectorizer = sklearn.feature_extraction.text.TfidfVectorizer(
        )

        # Preprocess the papers.
        print('Preprocess the papers in the corpus...')
        preprocessed_paper_texts = [
            ' '.join(self._nlp_utils.preprocess(paper['body'], lemmatize=False))
            for paper in tqdm.tqdm(self._corpus)
        ]

        # Train the TF-IDF model on the corpus of papers.
        print('Compute TF-IDF vectors for all papers in the corpus...')
        self._tfidf_vectorizer.fit(preprocessed_paper_texts)

        # Compute TF-IDF vector for each paper.
        tfidf_vectors = self._tfidf_vectorizer.transform(
            preprocessed_paper_texts)

        # Save a dictionary from DOIs to TF-IDF vectors.
        self._corpus_tfidf = dict(
            zip(map(lambda paper: paper['doi'], self._corpus), tfidf_vectors))

    def get_similarities(self, query: str):
        """Returns a list of pairs containing a paper and a similarity, sorted by descending similarity.
        Args:
            query: The text for which to compute the similarities.
        """
        query_tokens = self._nlp_utils.preprocess(query)
        query_vector = self._tfidf_vectorizer.transform(
            [' '.join(query_tokens)])

        similarities = {}
        for doi in self._corpus_tfidf.keys():
            norm_product = scipy.sparse.linalg.norm(
                query_vector) * scipy.sparse.linalg.norm(
                    self._corpus_tfidf[doi])
            if norm_product == 0.0:
                similarities[doi] = 0
            else:
                vector_product = query_vector.dot(
                    self._corpus_tfidf[doi].transpose())[0, 0]
                similarities[doi] = vector_product / norm_product

        papers_with_similarity = [
            (paper, similarities[paper['doi']]) for paper in self._corpus
        ]
        sorted_by_similarity = sorted(papers_with_similarity,
                                      key=lambda x: -x[1])

        return sorted_by_similarity