import time

import requests

#from utils.setup_utils import check_es_connection
#from utils.elasticsearch import es_request
from elasticsearch import Elasticsearch
import spacy
from gensim_load_models import load_model
import numpy as np

# Configurations:
from utils.elasticsearch import es_request

es_url = "http://localhost:9200"
es_fields = ["description", "title"]
es_index = "data_test"
vector_field = "word_embedding_1"
nlp = spacy.load("en_core_web_md")  # make sure to use larger package!


model_dict = {
    "w2v": {
        "file_path": "./models/word_embeddings/word2vec-google-news-subwords-300/word2vec-google-news-subwords-300.gz",
        "es_field": "word_embedding_1",
        "binary": True
    },
    "glove": {
        "file_path": "./models/word_embeddings/glove-wiki-gigaword-300/glove-wiki-gigaword-300.gz",
        "es_field": "word_embedding_2",
        "binary": False
    },
    "fasttext": {
        "file_path": "./models/word_embeddings/fasttext-wiki-news-subwords-300/fasttext-wiki-news-subwords-300.gz",
        "es_field": "word_embedding_3",
        "binary": False
    },
    "inter_sent": "sentence_embedding_1",
    "sent2v": "sentence_embedding_2"
}


def create_index_with_word_embeddings(es_url_, fields, index, nlp_spacy, model_name):
    model = load_model(model_name)
    print('Model {} has been loaded successfully'.format(model_name))
    global model_dict
    tic = time.perf_counter()
    if True:
        hits = 1
        from_ = 0
        documents = 0
        times = []
        while hits > 0:
            res = Elasticsearch(es_url_).search(
                index=index,
                body={
                    "_source": fields,
                    "size": 50,
                    "query": {
                        "bool": {
                            "must_not": [
                                {"exists": {
                                    "field": vector_field
                                }}
                            ]
                        }
                    }
                }
            )
            tic = time.perf_counter()

            hits_old = hits
            hits = res["hits"]["total"]['value']
            print(hits)
            from_ += 50
            #print("Handled documents: ", from_)
            strings, ids = prepare_vectoring(es_url_, index, res['hits']['hits'], ["description", "title"])
            handle_bulk(es_url_, index, nlp_spacy, strings, ids, res['hits']['hits'], model)

            toc = time.perf_counter()
            print(f"Embedding needs {toc - tic:0.4f} seconds for {hits_old - hits} documents")
            if hits_old != 1:
                documents += hits_old - hits
            times.append(float(f"{toc - tic:0.4f}"))
            print(documents)
            print(times)


def prepare_vectoring(es_url_, index, res, fields):

    strings, ids = [], []

    for item in res:
        temp = ""
        for field in fields:
            temp += item['_source'][field]

        ids.append(item['_id'])
        strings.append(temp)

    return strings, ids


def handle_bulk(es_url_, index, nlp_spacy, strings, ids, res, model):

    for string in range(len(strings)):
        if strings[string] != "":
            doc = {"doc": {}}
            temp_doc = nlp_spacy(strings[string])
            vectors = clean_text(temp_doc, model)[1]

            if len(vectors) == 0:
                doc["doc"]["embedded"] = False
            else:
                centroid_vector = calc_centroid(vectors)
                if type(centroid_vector) is np.ndarray:
                    doc["doc"][vector_field] = centroid_vector.tolist()

            r = ingest(doc, index, ids[string], es_url_)


def clean_text(doc, model):
    filtered_words = []
    vectors = []
    unknown = []
    for token in range(len(doc)):
        if doc[token].pos_ not in ["NUM", "SYM", "PUNCT"] and not doc[token].is_stop:
            try:
                filtered_words.append(token)
                vec = model.get_vector(str(doc[token].lemma_).lower())
                vectors.append(vec)
            except KeyError:
                unknown.append(doc[token].lemma_)

    return filtered_words, vectors


def calc_centroid(vectors_):
    return np.mean(vectors_, axis=0)


def ingest(data_, index, id_, es_url_):
    """
    Help function for ingestion in ES index. Eventually refraction later.
    todo: move in elasticsearch utils
    :param id_: id where to save the data object
    :param data_: json data object
    :param index: index name
    :param es_url_: url of elasticsearch instance
    :return: response of the request
    """
    if id_ is not None:
        url = es_url_ + "/" + index + '/_update/' + id_
        return es_request("POST", url, data_)
    else:
        url = es_url_ + "/" + index + "/_doc"
        return es_request("POST", url, data_)


def delete(es_url_, index, id_=None):
    """
    Help function to delete a document in elasticsearch index.
    todo: move in elasticsearch utils
    :param index: String, name of the es index
    :param es_url_: String, url of es instance
    :param id_: String, document id
    :return: response of the request
    """
    if id_ is not None:
        url = es_url_ + "/" + index + '/_doc/' + id_
        return requests.delete(url)

    else:
        # todo delete if finished
        url = es_url_ + "/" + index + '/_delete_by_query'
        query = {
            "query": {
                "match": {
                    "description": ""
                    }
                }
            }
        return es_request("POST", url, query)


if __name__ == "__main__":
    create_index_with_word_embeddings(es_url, es_fields, es_index, nlp, "glove")
