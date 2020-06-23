import nltk
import collections
import gensim.corpora

# Problem with stemming: word2vec doesn't allow you to look up stems (as far as I know), only proper words.
#def stem(text: str):
#    stemmer = nltk.stem.PorterStemmer()
#    words = nltk.wordpunct_tokenize(text)

class NlpUtils:

    def __init__(self):
        nltk.download('punkt')
        nltk.download('brown')
        nltk.download('averaged_perceptron_tagger')
        documents = nltk.corpus.brown.sents()
        self._brown_dict = gensim.corpora.Dictionary(documents)
        self._lemmatizer = nltk.stem.WordNetLemmatizer()

    def preprocess(self, text: str, lemmatize=True, vocabulary=None):
        text = gensim.utils.simple_preprocess(text, min_len=3)
        #text = self.remove_non_dict_words(text)
        text = self.remove_common_words(text)

        if lemmatize:
            text = self.lemmatize(text)

        if vocabulary:
            text = self.remove_non_vocabulary_words(text, vocabulary)
        
        return text

    def lemmatize(self, text_tokens):
        pos_tagged_tokens = nltk.pos_tag(text_tokens)

        return [self._lemmatizer.lemmatize(text_token[0], pos=self._get_wordnet_pos(text_token[1])) for text_token in pos_tagged_tokens]
  
    def _get_wordnet_pos(self, treebank_tag):
        if treebank_tag.startswith('J'):
            return nltk.corpus.wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return nltk.corpus.wordnet.VERB
        elif treebank_tag.startswith('N'):
            return nltk.corpus.wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return nltk.corpus.wordnet.ADV
        else:
            return nltk.corpus.wordnet.NOUN

    def remove_non_dict_words(self, text_tokens):
        #TODO This corpus does not contain inflected forms, I think. (For example, 'investigates' is removed from the string. But it shouldn't.)
        raise NotImplementedError

        #words = set(nltk.corpus.words.words())

        #return [w for w in text_tokens if w.lower() in words]


    def remove_common_words(self, text_tokens: str, num_words_to_remove=140):
        stop_words = []

        with open('./dewey/src/deweyengine/english_words_by_frequency.txt', 'r', encoding='utf-8') as f:
            line = f.readline()
            for _ in range(num_words_to_remove):
                line = f.readline()
                stop_word = line.split()
                stop_words.append(stop_word[0])

        return [word for word in text_tokens if word.lower() not in stop_words]
    
    def remove_non_vocabulary_words(self, text_tokens: str, vocabulary): 
        return [word for word in text_tokens if word.lower() in vocabulary]


    def get_document_frequency(self, word: str):
        if word not in self._brown_dict.token2id.keys():
            return 0
        else:
            word_id = self._brown_dict.token2id[word]
            #print('The word "' + self._brown_dict[word_id] + '" appears in', self._brown_dict.dfs[word_id],'documents')

            return self._brown_dict.dfs[word_id]


    def get_normalized_bag_of_words(self, text_tokens, scale_by_idf=False):
        #tokenized_text = gensim.utils.simple_preprocess(text)
        normalized_bag_of_words = collections.defaultdict(float)
        n_words = 0
        for word in text_tokens:
            normalized_bag_of_words[word] += 1
            n_words += 1
        
        if scale_by_idf:
            for word in normalized_bag_of_words.keys():
                # Scale by 1 / (1 + document_frequency) to avoid division by 0.
                normalized_bag_of_words[word] *= (1 / (1+self.get_document_frequency(word)))

        # Normalize so that the vector elements sum to 1.
        for word in normalized_bag_of_words.keys():
            normalized_bag_of_words[word] /= n_words
        
        return normalized_bag_of_words

