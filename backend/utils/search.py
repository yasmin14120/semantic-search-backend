#
# Search utilities
#
from backend.utils.elasticsearch import es_request
import spacy
import json
import numpy as np
from tensorflow.python.ops.numpy_ops import np_config

np_config.enable_numpy_behavior()
nlp = spacy.load("en_core_web_md")


def calc_vector(term, model, word_embedding=False):
    temp_doc = nlp(term)
    if word_embedding:
        vectors = word_vectoring(temp_doc, model)[1]
        centroid_vector = calc_centroid(vectors)
    else:
        centroid_vector = sentence_vectoring(temp_doc, model).tolist()
    return centroid_vector


def word_vectoring(doc, model):
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


def sentence_vectoring(doc, model):
    sentence = ""
    for token in range(len(doc)):
        if doc[token].pos_ not in ["NUM", "SYM", "PUNCT"] and not doc[token].is_stop:
            sentence += " " + str(doc[token].lemma_).lower()
    vector = model.get_vector(sentence)

    if model.get_name() == "infersent":
        if len(vector) > 1:
            vector = centroid_2(vector)
        else:
            vector = vector[0]
        vector = vector[:2048]

    elif model.get_name() == "use":
        if len(vector) == 1:
            vector = vector[0]
        else:
            vector = centroid_2(vector)

    return vector


# TODO replace with the optimization
def calc_centroid(vectors_):
    res_vec = []
    for dimension in range(len(vectors_[0])):
        res_vec.append(0.0)
        for vec in range(len(vectors_)):
            res_vec[dimension] += vectors_[vec][dimension]
        res_vec[dimension] = res_vec[dimension] / len(vectors_[0])
    return res_vec


def centroid_2(arr):
    return np.mean(arr, axis=0)


def search(query_vector, k, url, index, field_name, term):
    query = {
        "from": 0,
        "size": k,
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "doc['{}'].size() == 0 ? 0 : cosineSimilarity(params.query_vector, doc['{}']) + 1.0".format(field_name, field_name),
                    "params": {"query_vector": query_vector}
                }
            }
        }
    }

    url = url + index + "/_search"
    r = es_request("GET", url, query)
    return prepare_results(r, term)


def prepare_results(res, term):
    try:
        res = res.json()
        search_result = {
            "term": term,
            "results": res["hits"]["hits"],
            "total_hits": res["hits"]["total"]["value"]
        }
        return search_result
    except:
        print(res)
        raise Exception