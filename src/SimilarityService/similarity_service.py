import json
import flask

import similarity_measures
from paper_store import PaperStore

app = flask.Flask(__name__)

similarity_measure = None


def initialize(dataServiceUrl):
    global similarity_measure
    store = PaperStore(dataServiceUrl)
    similarity_measure = similarity_measures.TfIdfSimilarityCorpus(
        corpus=store.get_all()[:3])


@app.route('/search', methods=['POST'])
def get_papers_by_similarity():
    received_json = flask.request.json
    query = json.loads(received_json)['query']
    print('Computing similarities...')
    papers_with_similarity = similarity_measure.get_similarities(query)
    print('Done.')

    return flask.jsonify(papers_with_similarity)


'''
@app.route('/updatesummaries', methods=['POST'])
def update_all_summaries():
    _nlp_utils = nlp_utils.NlpUtils()
    for paper in tqdm.tqdm(self._store.get_all()):
        self._store.delete(paper['doi'])
        paper['auto_summary'] = _nlp_utils.get_summary_tfidf(paper['body'])
        self._store.insert(paper)
'''

if __name__ == '__main__':
    initialize(dataServiceUrl='http://127.0.0.1:8080/')
    app.run(port=8081)

    # Now, could talk to this service as follows:
    #response = requests.post('http://127.0.0.1:8081/search',
    #                         json='{ "query": "asdf" }')
    #similarity_response_json = response.text
    #parsed_response = json.loads(similarity_response_json)