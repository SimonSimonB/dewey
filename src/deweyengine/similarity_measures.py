import pathlib
import tqdm
import scipy.sparse.linalg
import sklearn
import typing
import nltk
import collections
import numpy
import gensim
import nlp_utils

BIG_MODEL = False
WORD2VEC_MODEL_PATH = pathlib.Path("C:/Users/simon/Coding/ML/models")

class CosineSimilarity:

    def __init__(self):
        if BIG_MODEL:
            self._model = gensim.models.KeyedVectors.load_word2vec_format(WORD2VEC_MODEL_PATH / 'GoogleNews-vectors-negative300.bin', binary=True)
        else:
            self._model = gensim.models.KeyedVectors.load_word2vec_format(WORD2VEC_MODEL_PATH / 'GoogleNews-vectors-negative300.bin', binary=True, limit=100000)
            #my_docs = ["Who let the dogs out?", "Who? Who? Who? Who?"]
            #tokenized_list = [gensim.utils.simple_preprocess(doc) for doc in my_docs]
            #mydict = gensim.corpora.Dictionary(tokenized_list)
            #mycorpus = [mydict.doc2bow(doc, allow_update=True) for doc in tokenized_list]
            #model = gensim.models.LdaModel(mycorpus, 10)
        
        self._nlp_tools = nlp_utils.NlpUtils()
        
    def get_similarity(self, query, paper, most_common=None):

        ## Process the query.
        query_tokens = self._nlp_tools.preprocess(query, vocabulary=self._model)
        query_nbow = self._nlp_tools.get_normalized_bag_of_words(query_tokens, scale_by_idf=True)
        #print(sorted(query_nbow, key=lambda word: query_nbow[word], reverse=True)[:20])
        query_sum_embeddings = sum(self._model[word] * query_nbow[word] for word in query_nbow.keys())

        ## Process the paper.
        paper_tokens = self._nlp_tools.preprocess(5*(paper['abstract'] + ' ') + paper['body'], self._model)
        paper_nbow = self._nlp_tools.get_normalized_bag_of_words(paper_tokens, scale_by_idf=True)

        # Add words in title to the bag of words, as if they were as significant as the most common word from the body.
        max_significance = paper_nbow[sorted(paper_nbow, key=lambda word: paper_nbow[word], reverse=True)[0]]
        for word in self._nlp_tools.preprocess(paper['title'], vocabulary=self._model):
            paper_nbow[word] = max_significance

        paper_sum_embeddings = sum(self._model[word] * paper_nbow[word] for word in paper_nbow.keys())
        print(self._model.similar_by_vector(paper_sum_embeddings))

        ## Cosine similarity based on sum embeddings.
        if numpy.linalg.norm(query_sum_embeddings)*numpy.linalg.norm(paper_sum_embeddings) == 0.0:
            similarity = 0
        else:
            similarity = numpy.dot(query_sum_embeddings, paper_sum_embeddings)/(numpy.linalg.norm(query_sum_embeddings)*numpy.linalg.norm(paper_sum_embeddings))
        
        ## Cosine similarity based on pairwise comparison of embeddings of top N elements in bags of words.
        '''
        N = 20
        similarity = 0
        for doc_word in sorted(paper_nbow, key=lambda word: paper_nbow[word], reverse=True)[:N]:
            for word in sorted(query_nbow, key=lambda word: query_nbow[word], reverse=True)[:N]:
                cosine_similarity = numpy.dot(self._model[doc_word], self._model[word])/(numpy.linalg.norm(self._model[doc_word])*numpy.linalg.norm(self._model[word]))
                similarity += paper_nbow[doc_word] * query_nbow[word] * cosine_similarity
        '''

        return similarity
    
"""
class SpacySimilarity():

    def __init__(self):
        self._nlp = spacy.load('en_core_web_lg')
    
    def get_similarity(self, text1: str, text2: str):
        doc1 = self._nlp(text1)
        doc2 = self._nlp(text2)
        return doc1.similarity(doc2)
"""

class TfIdfSimilarityCorpus():

    def __init__(self, corpus: typing.Iterable[dict]):
        self._corpus = list(corpus)
        self._nlp_utils = nlp_utils.NlpUtils()
        self._tfidf_vectorizer = sklearn.feature_extraction.text.TfidfVectorizer()

        # Preprocess the papers.
        print('Preprocess the papers in the corpus...')
        preprocessed_paper_texts = [' '.join(self._nlp_utils.preprocess(paper['body'], lemmatize=False)) for paper in tqdm.tqdm(self._corpus)]

        # Train the TF-IDF model on the corpus of papers.
        print('Compute TF-IDF vectors for all papers in the corpus...')
        self._tfidf_vectorizer.fit(preprocessed_paper_texts)

        # Compute TF-IDF vector for each paper.
        tfidf_vectors = self._tfidf_vectorizer.transform(preprocessed_paper_texts)

        # Save a dictionary from DOIs to TF-IDF vectors.
        self._corpus_tfidf = dict(zip(map(lambda paper: paper['doi'], self._corpus), tfidf_vectors))


    def get_similarities(self, query: str):
        """Returns a list of pairs containing a paper and a similarity, sorted by descending similarity.
        Args:
            query: The text for which to compute the similarities.
        """
        query_tokens = self._nlp_utils.preprocess(query)
        query_vector = self._tfidf_vectorizer.transform([' '.join(query_tokens)])

        similarities = {}
        for doi in self._corpus_tfidf.keys():
            norm_product = scipy.sparse.linalg.norm(query_vector) * scipy.sparse.linalg.norm(self._corpus_tfidf[doi])
            if norm_product == 0.0:
                similarities[doi] = 0
            else:
                vector_product = query_vector.dot(self._corpus_tfidf[doi].transpose())[0, 0]
                similarities[doi] = vector_product / norm_product
        
        papers_with_similarity = [(paper, similarities[paper['doi']]) for paper in self._corpus]
        sorted_by_similarity = sorted(papers_with_similarity, key = lambda x: -x[1])
        
        return sorted_by_similarity


class TfIdfSimilarity():

    def __init__(self, corpus: typing.Iterable[str]):
        self._corpus = corpus
        self._nlp_utils = nlp_utils.NlpUtils()

        self._tfidf_vectorizer = sklearn.feature_extraction.text.TfidfVectorizer()

        # TODO: Preprocess texts before fitting the vectorizer to them!
        self._tfidf_vectorizer.fit(self._corpus)

    def get_similarity(self, query: str, paper):
        query_tokens = self._nlp_utils.preprocess(query)
        paper_tokens = self._nlp_utils.preprocess(paper['body'])

        query_vector = self._tfidf_vectorizer.transform([' '.join(query_tokens)])
        paper_vector = self._tfidf_vectorizer.transform([' '.join(paper_tokens)])

        norm_product = scipy.sparse.linalg.norm(query_vector) * scipy.sparse.linalg.norm(paper_vector)
        if norm_product == 0.0:
            similarity = 0
        else:
            vector_product = query_vector.dot(paper_vector.transpose())[0, 0]
            similarity = vector_product / norm_product

        return similarity
