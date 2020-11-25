import os
import nltk
import itertools
import re
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
        #self._summarizer = summarizer.Summarizer()

        words_by_frequency_path = os.path.join(
            os.path.dirname(__file__), 'english_words_by_frequency.txt')
        self._stop_words = []
        with open(words_by_frequency_path, 'r', encoding='unicode_escape') as f:
            # Skip the first line, which contains the names of the columns.
            line = f.readline()
            for line in f:
                stop_word = line.split()
                self._stop_words.append(stop_word[0])

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

        return [
            self._lemmatizer.lemmatize(text_token[0],
                                       pos=self._get_wordnet_pos(text_token[1]))
            for text_token in pos_tagged_tokens
        ]

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
        return [
            word for word in text_tokens if word.lower() not in self._stop_words
        ]

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
                normalized_bag_of_words[word] *= (
                    1 / (1 + self.get_document_frequency(word)))

        # Normalize so that the vector elements sum to 1.
        for word in normalized_bag_of_words.keys():
            normalized_bag_of_words[word] /= n_words

        return normalized_bag_of_words

    def get_summary_bert(self, text: str):
        shortening_factor = 700 / len(text)
        return self._summarizer(text, ratio=shortening_factor)

    def get_summary_tfidf(self,
                          text,
                          text_tokens=None,
                          max_summary_words=100,
                          word_idfs=None):
        # Tokenizing the text
        if not text_tokens:
            text_tokens = self.preprocess(text, lemmatize=False)

        freq_table = collections.defaultdict(int)
        for word in text_tokens:
            word = word.lower()
            freq_table[word] += 1

        # Creating a dictionary to keep the score of each sentence
        sentences = nltk.tokenize.sent_tokenize(text)
        # Throw out sentences which contain multiple capitalized letters next to each other (indicates that it includes section headings).
        sentences = [
            sentence for sentence in sentences
            if not re.search('[A-Z]+[A-Z]+', sentence)
        ]
        # Throw out sentences with fewer five words.
        sentences = [
            sentence for sentence in sentences
            if not len(nltk.tokenize.word_tokenize(sentence)) < 5
        ]
        # Throw out sentences which contain proper names, such as 'The Difference Principle' or 'Instrumental Premise', by throwing out all sentences with more than two upper case letters.
        sentences = [
            sentence for sentence in sentences
            if not sum(1 for c in sentence if c.isupper()) > 2
        ]
        sentence_value = collections.defaultdict(float)

        # Extract sentences which summarize or contain statements about what the paper argues for
        candidate_sentences = []
        for sentence in sentences:
            nouns = ['I', 'We', 'we', 'paper', 'essay']
            verbs = [
                'argue', 'show', 'demonstrate', 'suggest', 'conclude',
                'draw the conclusion', 'draws the conclusion'
            ]
            high_value_phrases = [
                noun + ' ' + verb
                for noun, verb in itertools.product(nouns, verbs)
            ] + [
                noun + ' will ' + verb
                for noun, verb in itertools.product(nouns, verbs)
            ] + [
                noun + ' shall ' + verb
                for noun, verb in itertools.product(nouns, verbs)
            ] + [
                ' section', ' Section', 'sum up', 'In conclusion, ', 'To recap',
                'To summarize'
            ]
            if any(high_value_phrase in sentence
                   for high_value_phrase in high_value_phrases):
                candidate_sentences.append(sentence)

        # TODO Compute tf-idf using corpus
        for sentence in candidate_sentences:
            # Compute average tf score for each candidate sentence.
            sentence_words = self.preprocess(sentence, lemmatize=False)
            sentence_words = set(sentence_words) - set(high_value_phrases)
            for word in sentence_words:
                if word in freq_table.keys():
                    sentence_value[sentence] += freq_table[word]

            sentence_value[sentence] /= len(
                nltk.tokenize.word_tokenize(sentence))

        sorted_sentences = sorted(candidate_sentences,
                                  key=lambda sentence: sentence_value[sentence],
                                  reverse=True)

        # Extract the top sentences
        sentences_in_summary = []
        sentence_value_threshold = 3
        for sentence in sorted_sentences:
            if sentence_value[sentence] < sentence_value_threshold:
                print(f'BELOW THRESHOLD: {sentence}')
                continue
            elif sum(
                    len(nltk.tokenize.word_tokenize(sentence))
                    for sentence in sentences_in_summary
            ) + len(nltk.tokenize.word_tokenize(sentence)) > max_summary_words:
                continue
            else:
                sentences_in_summary.append(sentence)

        # Return the top sentences in the order they appear in the text.
        sentences_in_summary = sorted(sentences_in_summary, key=sentences.index)

        return ' [...] '.join(sentences_in_summary)