import json
import time
import numpy as np
import requests

#from utils.setup_utils import check_es_connection
#from utils.elasticsearch import es_request
from elasticsearch import Elasticsearch
import spacy
from encoder.infersent_load_model import load_model
from word_embeddings import prepare_vectoring
#from universal_sentence_encoder.load_use import load_modul


es_url = "http://localhost:9200"
es_fields = ["description", "title"]
es_index = "data_test"
infersent_field = "sentence_embedding_1"
infersent_2_field = "sentence_embedding_3"  # für die wort optimierungen
infersent_3_field = "sentence_embedding_4"  # für verbesserten dim compressions vektor
use_field = "sentence_embedding_2"
path_infersent = "encoder/infersent1.pkl"
path_glove = "/home/user/gensim-data/glove-wiki-gigaword-300/glove-wiki-gigaword-300.txt"
nlp = spacy.load("en_core_web_md")  # make sure to use larger package!
path_use = "universal-sentence-encoder_4"

import tensorflow_hub as hub


def load_use(path):
    return hub.load(path)


def create_index_with_sentence_embeddings(es_url_, fields, index, nlp_spacy, model_name):
    global path_glove
    global path_infersent

    #model = load_model(path_infersent=path_infersent, path_word_vector=path_glove)
    model = load_use(path_use)

    if True:
        hits = 1
        from_ = 0
        documents = 0
        times = []
        error_counter = 0
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
                                    "field": "sentence_embedding_2"
                                }}
                            ]
                        }}
                }
            )
            tic = time.perf_counter()
            hits_old = hits
            hits = res["hits"]["total"]['value']
            from_ += 50
            print("Handled documents: ", from_)

            strings, ids = prepare_vectoring(es_url_, index, res['hits']['hits'], ["title", "description"])
            vectors = clean_text(strings, model)
            ids = handle_bulk(es_url_, index, ids, res['hits']['hits'], vectors)
            error_counter += len(ids)

            toc = time.perf_counter()
            print(f"Embedding needs {toc - tic:0.4f} seconds for {hits_old - hits} documents")
            if hits_old != 1:
                documents += hits_old - hits
            times.append(float(f"{toc - tic:0.4f}"))
            print(documents)
            print(times)


def handle_bulk(es_url_, index, ids, res, vectors):
    errors = []
    docs = ""
    if len(vectors) == 0:
        errors = ids
    tic = time.perf_counter()

    for i in range(len(res)):

        if len(vectors[i]) == 0:
            errors.append(ids[i])
        else:
            doc = {"doc": {use_field: []}}
            centroid_vector = centroid_2(vectors[i])

            if type(centroid_vector) is np.ndarray:
                doc["doc"][use_field] = centroid_vector.tolist()[:2048]
                docs += json.dumps(bulk_load_pre(index, ids[i])) + "\n"
                docs += json.dumps(doc) + "\n"

    toc = time.perf_counter()
    print(f"Calc centroid vector needs {toc - tic:0.4f} seconds")

    for i in range(len(errors)):
        doc = {"doc": {"embedded": False}}
        docs += json.dumps(bulk_load_pre(index, errors[i])) + "\n"
        docs += json.dumps(doc) + "\n"

    r = requests.post(es_url_ + "/" + index + "/_doc/_bulk",
                      headers={"content-type": "application/json"},
                      data=docs)
    return errors


def bulk_load_pre(index, id):
    return {"update": {"_index": index, "_id": id}}


def clean_text_2(strings, model):
    vectors, errors = [], []
    for doc in range(len(strings)):
        # string cleaning
        sentence = ""
        for token in nlp(strings[doc]):
            if token.pos_ not in ["NUM", "SYM"] and not token.is_stop:
                sentence += " " + str(token.lemma_).lower()
        try:
            vector = model.encode(strings[doc], bsize=64, tokenize=False, verbose=False)
        except Exception as e:
            print("EXCEPTION: ", e)
            vector = []
        vectors.append(vector)

    return vectors


def clean_text(strings, model):
    sentences, doc_indices = [], []
    sentence_counter = 0
    for doc in range(len(strings)):
        sents = nlp(strings[doc]).sents
        for i in sents:
            if str(i) != "":
                sentences.append(str(i).lower())
                sentence_counter += 1
        doc_indices.append(sentence_counter)

    try:
        vectors = model.encode(sentences, bsize=64, tokenize=False, verbose=False)
       
    except Exception:
        vectors = []
        errors = []

    errors = []
    deletes_per_doc = []
    handles_errors = 0
    for i in doc_indices:
        start = 0
        for err in range(handles_errors, len(errors)):
            if errors[err] < i:
                start += 1
                handles_errors += 1
            else:
                break
        deletes_per_doc.append(start)
        if handles_errors > len(errors):
            break

    doc_indices = [doc_indices[i] - deletes_per_doc[i] for i in range(len(doc_indices))]
    result = []
    prev = 0
    for index in doc_indices:
        if index - prev == 0:
            result.append([])
        else:
            result.append(vectors[prev:index])
        prev = index
    return result


def centroid_np(arr):
    length, dim = arr.shape
    return np.array([np.sum(arr[:, i])/length for i in range(dim)])


def centroid_2(arr):
    return np.mean(arr, axis=0)


if __name__ == "__main__":
    create_index_with_sentence_embeddings(es_url, es_fields, es_index, nlp, "use")
