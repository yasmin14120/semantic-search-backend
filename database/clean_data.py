# created by user
# Modul is used to clean data and ingest into es index

import spacy
import numpy as np
import json
from elasticsearch import es_request

ES_URL = "http://localhost:9200/"


def clean_string(string, symbol_array):
    return ''.join([c for c in string if c not in symbol_array])


def ingest(data_, index):
    url = ES_URL + index + "/_doc"
    return es_request("POST", url, data_)


if __name__ == "__main__":
    with open("datasets/meta_Books.json", "r") as f:
        i = 0
        for row in f:
            if i > 10000:
                break

            data_ = json.loads(row)
            if len(data_['description']) > 0:
                data = {"description": clean_string(data_['description'][0], ['\t', '\n', '\'', '\"']), "title": clean_string(data_['title'], ['\"', '\''])}
                r = ingest(data, "data_test")
                i += 1
        f.close()
